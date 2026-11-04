from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
    # Mark all as read when user opens the list
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.related_request:
        return redirect('requests_app:request_detail', pk=notif.related_request.pk)
    return redirect('notifications:list')
