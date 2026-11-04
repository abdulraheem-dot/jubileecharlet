"""
notifications/utils.py

Helper functions for creating notifications.
Imported by other apps to send notifications without circular imports.
"""

from .models import Notification


def create_notification(recipient, title, message, request_obj=None, notification_type='GENERAL'):
    """Create a single notification for a user."""
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        related_request=request_obj,
        notification_type=notification_type
    )


def notify_staff_new_request(request_obj):
    """Notify all receptionists and managers of a new request."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    staff = User.objects.filter(
        role__in=['RECEPTIONIST', 'MANAGER', 'SUPER_ADMIN'],
        is_active=True
    )
    for user in staff:
        create_notification(
            recipient=user,
            title=f"New Request — Room {request_obj.room.number}",
            message=f"{request_obj.title} ({request_obj.get_priority_display()})",
            request_obj=request_obj,
            notification_type='NEW_REQUEST'
        )


def notify_guest_status_change(request_obj):
    """Notify the guest that their request status has changed."""
    if request_obj.guest and request_obj.guest.user:
        create_notification(
            recipient=request_obj.guest.user,
            title=f"Request Update — #{request_obj.request_number}",
            message=f"Your request '{request_obj.title}' is now {request_obj.get_status_display()}.",
            request_obj=request_obj,
            notification_type='STATUS_CHANGE'
        )
