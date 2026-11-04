from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import WebsiteSettings
from .serializers import WebsiteSettingsSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_settings(request):
    settings_obj = WebsiteSettings.get_settings()
    return Response(WebsiteSettingsSerializer(settings_obj).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_summary_admin(request):
    """Admin-only overview stats."""
    if not request.user.is_authenticated or not request.user.is_staff:
        from rest_framework import status
        return Response({'message': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    from bookings.models import Booking
    from enquiries.models import ContactEnquiry
    from django.utils import timezone

    today = timezone.now().date()
    bookings = Booking.objects.all()

    return Response({
        'total_bookings': bookings.count(),
        'today_arrivals': bookings.filter(check_in_date=today, status__in=['confirmed', 'checked_in']).count(),
        'today_departures': bookings.filter(check_out_date=today, status='checked_in').count(),
        'pending_bookings': bookings.filter(status__in=['pending', 'awaiting_payment']).count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
        'unread_enquiries': ContactEnquiry.objects.filter(status='new').count(),
    })
