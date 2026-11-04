from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import HousekeepingTask
from rooms.models import Room, HousekeepingStatus


@login_required
def dashboard(request):
    today = timezone.now().date()
    tasks = HousekeepingTask.objects.filter(
        scheduled_date=today
    ).select_related('room', 'assigned_to').order_by('status', 'room__number')

    # Only show tasks assigned to this user if they're housekeeping staff
    if request.user.role == 'HOUSEKEEPING':
        tasks = tasks.filter(assigned_to=request.user)

    rooms_needing_attention = Room.objects.filter(
        housekeeping_status__in=['DIRTY', 'CLEANING']
    ).order_by('floor', 'number')

    context = {
        'tasks':                    tasks,
        'rooms_needing_attention':  rooms_needing_attention,
        'pending_count':            tasks.filter(status='PENDING').count(),
        'in_progress_count':        tasks.filter(status='IN_PROGRESS').count(),
        'completed_count':          tasks.filter(status='COMPLETED').count(),
    }
    return render(request, 'housekeeping/dashboard.html', context)


@login_required
def update_task(request, pk):
    task = get_object_or_404(HousekeepingTask, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'IN_PROGRESS':
            task.status     = 'IN_PROGRESS'
            task.started_at = timezone.now()
            task.room.housekeeping_status = HousekeepingStatus.CLEANING
            task.room.save()
        elif new_status == 'COMPLETED':
            task.status      = 'COMPLETED'
            task.completed_at = timezone.now()
            task.room.housekeeping_status = HousekeepingStatus.CLEANED
            task.room.save()
        task.save()
        messages.success(request, "Task updated.")
    return redirect('housekeeping:dashboard')


@login_required
def room_status_overview(request):
    """Shows all rooms and their housekeeping status."""
    rooms = Room.objects.select_related('room_type').order_by('floor', 'number')
    return render(request, 'housekeeping/room_status.html', {'rooms': rooms})
