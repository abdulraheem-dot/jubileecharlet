from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter, BooleanFilter
from django.db.models import Q

from .models import Room, RoomCategory
from .serializers import RoomListSerializer, RoomDetailSerializer, RoomCategorySerializer


class RoomFilter(FilterSet):
    min_price = NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = NumberFilter(field_name='price_per_night', lookup_expr='lte')
    max_occupancy = NumberFilter(field_name='max_occupancy', lookup_expr='gte')
    category = CharFilter(field_name='category__slug')

    class Meta:
        model = Room
        fields = ['category', 'min_price', 'max_price', 'max_occupancy', 'is_available']


class RoomListView(generics.ListAPIView):
    serializer_class = RoomListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RoomFilter
    ordering_fields = ['price_per_night', 'max_occupancy', 'name']
    ordering = ['category', 'price_per_night']

    def get_queryset(self):
        return (
            Room.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('images', 'amenities')
        )


class RoomDetailView(generics.RetrieveAPIView):
    serializer_class = RoomDetailSerializer
    permission_classes = [AllowAny]
    queryset = Room.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'amenities')
    lookup_field = 'slug'


class RoomCategoryListView(generics.ListAPIView):
    serializer_class = RoomCategorySerializer
    permission_classes = [AllowAny]
    queryset = RoomCategory.objects.all()
    pagination_class = None


@api_view(['GET'])
@permission_classes([AllowAny])
def check_availability(request):
    """
    Return rooms available for the given date range and guest count.
    Rooms are unavailable if they have a confirmed/checked_in booking
    that overlaps with the requested dates.
    """
    from bookings.models import Booking

    check_in = request.query_params.get('check_in')
    check_out = request.query_params.get('check_out')
    num_adults = int(request.query_params.get('num_adults', 1))
    num_children = int(request.query_params.get('num_children', 0))

    if not check_in or not check_out:
        return Response({'message': 'check_in and check_out are required.'}, status=400)

    if check_in >= check_out:
        return Response({'message': 'check_out must be after check_in.'}, status=400)

    # Find rooms that are booked during this period
    booked_room_ids = (
        Booking.objects
        .filter(
            status__in=['confirmed', 'checked_in', 'awaiting_payment', 'pending'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
        )
        .values_list('booking_rooms__room_id', flat=True)
    )

    available_rooms = list(
        Room.objects
        .filter(is_active=True, is_available=True)
        .filter(max_adults__gte=num_adults)
        .exclude(id__in=booked_room_ids)
        .select_related('category')
        .prefetch_related('images', 'amenities')
    )

    # Also consult the PMS so rooms physically out of service (maintenance,
    # occupied by walk-ins, etc.) are excluded from search results. This is a
    # safe no-op if the PMS isn't configured or is unreachable.
    from integrations.services import get_pms_unavailable_rooms
    pms_unavailable = set(get_pms_unavailable_rooms(available_rooms, check_in, check_out))
    if pms_unavailable:
        available_rooms = [r for r in available_rooms if r.name not in pms_unavailable]

    serializer = RoomListSerializer(available_rooms, many=True, context={'request': request})
    return Response(serializer.data)
