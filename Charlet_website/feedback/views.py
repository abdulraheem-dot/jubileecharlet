from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Feedback, Complaint
from accounts.decorators import manager_required


@login_required
@manager_required
def feedback_list(request):
    feedbacks   = Feedback.objects.select_related('request', 'guest').order_by('-created_at')
    complaints  = Complaint.objects.select_related('room', 'guest', 'assigned_to').order_by('-created_at')

    open_complaints = complaints.filter(status__in=['OPEN', 'IN_REVIEW'])

    from django.db.models import Avg
    avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0

    context = {
        'feedbacks':        feedbacks[:20],
        'complaints':       complaints[:20],
        'open_complaints':  open_complaints,
        'avg_rating':       round(avg_rating, 1),
        'total_feedback':   feedbacks.count(),
    }
    return render(request, 'feedback/list.html', context)


# Guest-facing feedback form
def guest_feedback(request, request_pk):
    from requests_app.models import ServiceRequest
    req = get_object_or_404(ServiceRequest, pk=request_pk, status='COMPLETED')

    room_id = request.session.get('guest_room_id')
    if not room_id or req.room.pk != room_id:
        return redirect('guests:portal_home')

    if hasattr(req, 'feedback'):
        return redirect('guests:portal_home')

    if request.method == 'POST':
        rating  = int(request.POST.get('rating', 3))
        comment = request.POST.get('comment', '')
        if req.guest:
            Feedback.objects.create(request=req, guest=req.guest, rating=rating, comment=comment)
        messages.success(request, "Thank you for your feedback!")
        return redirect('guests:portal_home')

    return render(request, 'feedback/guest_feedback.html', {'req': req})


# Guest complaint submission
def guest_complaint(request):
    room_id = request.session.get('guest_room_id')
    stay_id = request.session.get('guest_stay_id')
    if not room_id:
        return redirect('guests:portal_entry')

    from rooms.models import Room
    from guests.models import GuestStay
    room  = get_object_or_404(Room, pk=room_id)
    stay  = GuestStay.objects.filter(pk=stay_id, is_active=True).select_related('guest').first() if stay_id else None
    guest = stay.guest if stay else None

    if not guest:
        messages.error(request, "Please check in before submitting a complaint.")
        return redirect('guests:portal_home')

    if request.method == 'POST':
        Complaint.objects.create(
            guest=guest,
            room=room,
            category=request.POST.get('category', 'OTHER'),
            description=request.POST.get('description', ''),
            priority=request.POST.get('priority', 'NORMAL'),
        )
        # Notify management
        try:
            from notifications.utils import create_notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            for mgr in User.objects.filter(role__in=['MANAGER', 'SUPER_ADMIN'], is_active=True):
                create_notification(mgr, f"New complaint — Room {room.number}",
                                    f"Category: {request.POST.get('category')}", notification_type='URGENT')
        except Exception:
            pass
        messages.success(request, "Your complaint has been submitted. We will contact you shortly.")
        return redirect('guests:portal_home')

    return render(request, 'feedback/guest_complaint.html', {
        'room': room,
        'categories': Complaint.Category.choices,
    })
