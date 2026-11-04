import logging
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter

from accommodation.models import Room
from .models import Booking, BookingRoom, CancellationRequest
from .serializers import BookingSerializer, CreateBookingSerializer, CancellationRequestSerializer

logger = logging.getLogger('jubilee')


class BookingFilter(FilterSet):
    status = CharFilter(field_name='status')

    class Meta:
        model = Booking
        fields = ['status']


def check_room_availability(room_ids, check_in, check_out, exclude_booking_id=None):
    """
    Return True if all rooms are available for the period.
    Uses SELECT FOR UPDATE to prevent concurrent double-booking.
    """
    conflict_qs = (
        Booking.objects
        .filter(
            status__in=['pending', 'awaiting_payment', 'confirmed', 'checked_in'],
            booking_rooms__room_id__in=room_ids,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
        )
    )
    if exclude_booking_id:
        conflict_qs = conflict_qs.exclude(pk=exclude_booking_id)
    return not conflict_qs.exists()


class BookingListCreateView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Booking.objects
            .filter(guest=self.request.user)
            .prefetch_related('booking_rooms__room__images', 'booking_rooms__room__category')
        )

    def post(self, request, *args, **kwargs):
        serializer = CreateBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        room_ids = data['room_ids']
        check_in = data['check_in_date']
        check_out = data['check_out_date']

        # Validate rooms exist and are active
        rooms = Room.objects.filter(id__in=room_ids, is_active=True, is_available=True)
        if rooms.count() != len(set(room_ids)):
            return Response(
                {'message': 'One or more selected rooms are unavailable or do not exist.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate occupancy
        for room in rooms:
            if data['num_adults'] > room.max_adults:
                return Response(
                    {'message': f'{room.name} can accommodate a maximum of {room.max_adults} adult(s).'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Consult the inner management system (PMS) for physical availability.
        # The PMS is the source of truth for room status (maintenance,
        # out-of-service, occupied by walk-ins).  If it's unreachable or not
        # configured this is a safe no-op so booking still works standalone.
        from integrations.services import get_pms_unavailable_rooms
        pms_unavailable = get_pms_unavailable_rooms(list(rooms), check_in, check_out)
        if pms_unavailable:
            return Response(
                {'message': f'The following rooms are currently unavailable: {", ".join(pms_unavailable)}.'},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            with transaction.atomic():
                # Lock rooms to prevent concurrent booking
                locked_rooms = Room.objects.select_for_update().filter(id__in=room_ids)

                if not check_room_availability(room_ids, check_in, check_out):
                    return Response(
                        {'message': 'One or more of the selected rooms is no longer available for your dates.'},
                        status=status.HTTP_409_CONFLICT,
                    )

                booking = Booking.objects.create(
                    guest=request.user,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    num_adults=data['num_adults'],
                    num_children=data['num_children'],
                    special_requests=data.get('special_requests', ''),
                    status=Booking.Status.AWAITING_PAYMENT,
                )

                for room in locked_rooms:
                    BookingRoom.objects.create(
                        booking=booking,
                        room=room,
                        price_per_night=room.price_per_night,
                    )

                booking.calculate_totals()
                booking.save()

                logger.info('Booking created: %s for user %s', booking.booking_reference, request.user.email)

        except Exception as exc:
            logger.exception('Booking creation failed: %s', exc)
            return Response(
                {'message': 'Booking could not be created. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        result = Booking.objects.prefetch_related(
            'booking_rooms__room__images', 'booking_rooms__room__category'
        ).get(pk=booking.pk)
        return Response(BookingSerializer(result).data, status=status.HTTP_201_CREATED)


class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own bookings
        return Booking.objects.filter(guest=self.request.user).prefetch_related(
            'booking_rooms__room__images', 'booking_rooms__room__category'
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_cancellation(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, guest=request.user)
    except Booking.DoesNotExist:
        return Response({'message': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status not in ['pending', 'awaiting_payment', 'confirmed']:
        return Response(
            {'message': 'This booking cannot be cancelled in its current state.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if hasattr(booking, 'cancellation_request'):
        return Response({'message': 'A cancellation request already exists for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

    reason = request.data.get('reason', '')
    CancellationRequest.objects.create(booking=booking, reason=reason)
    booking.status = Booking.Status.CANCELLATION_REQUESTED
    booking.save()

    logger.info('Cancellation requested: %s', booking.booking_reference)
    return Response({'message': 'Cancellation request submitted successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user_bookings = Booking.objects.filter(guest=request.user)
    today = timezone.now().date()

    return Response({
        'total_bookings': user_bookings.count(),
        'upcoming_bookings': user_bookings.filter(
            status__in=['confirmed', 'awaiting_payment'],
            check_in_date__gte=today,
        ).count(),
        'past_bookings': user_bookings.filter(status='checked_out').count(),
        'pending_bookings': user_bookings.filter(status__in=['pending', 'awaiting_payment']).count(),
        'cancelled_bookings': user_bookings.filter(status='cancelled').count(),
    })
