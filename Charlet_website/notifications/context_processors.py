"""
notifications/context_processors.py

A context processor injects variables into EVERY template automatically.
We registered this in settings.py under TEMPLATES > context_processors.

This means every template can use {{ unread_notification_count }}
and {{ unread_request_count }} without the view explicitly passing them.

Django calls this function on every request and merges the returned
dictionary into the template context.
"""


def notification_count(request):
    """
    Returns unread notification and request counts for the logged-in user.
    These appear in the sidebar badge and the notification bell icon.
    """
    context = {
        'unread_notification_count': 0,
        'unread_request_count': 0,
    }

    if not request.user.is_authenticated:
        return context

    try:
        from notifications.models import Notification
        context['unread_notification_count'] = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    except Exception:
        pass

    try:
        from requests_app.models import ServiceRequest
        if request.user.can_manage_requests:
            context['unread_request_count'] = ServiceRequest.objects.filter(
                status='NEW'
            ).count()
    except Exception:
        pass

    return context
