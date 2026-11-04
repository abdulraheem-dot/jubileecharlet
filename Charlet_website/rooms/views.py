from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

from .models import Room, RoomType, RoomStatus, HousekeepingStatus
from accounts.decorators import manager_required, receptionist_or_above


@login_required
@receptionist_or_above
def room_list(request):
    """
    Shows all rooms with their current status.

    Q objects allow complex queries with AND / OR logic:
    Q(status='AVAILABLE') | Q(status='RESERVED')  →  status=AVAILABLE OR RESERVED

    .annotate() adds computed fields to each object in the QuerySet.
    Here we count how many active requests each room has.
    """
    rooms = Room.objects.select_related('room_type').order_by('floor', 'number')

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        rooms = rooms.filter(status=status_filter)

    # Filter by floor
    floor_filter = request.GET.get('floor', '')
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)

    # Search by room number
    search = request.GET.get('q', '')
    if search:
        rooms = rooms.filter(number__icontains=search)

    # Summary counts for the top stat cards
    summary = {
        'total':       Room.objects.count(),
        'available':   Room.objects.filter(status=RoomStatus.AVAILABLE).count(),
        'occupied':    Room.objects.filter(status=RoomStatus.OCCUPIED).count(),
        'cleaning':    Room.objects.filter(status=RoomStatus.CLEANING).count(),
        'maintenance': Room.objects.filter(status=RoomStatus.MAINTENANCE).count(),
    }

    floors = Room.objects.values_list('floor', flat=True).distinct().order_by('floor')

    context = {
        'rooms':         rooms,
        'summary':       summary,
        'status_choices': RoomStatus.choices,
        'status_filter': status_filter,
        'floor_filter':  floor_filter,
        'floors':        floors,
        'search':        search,
    }
    return render(request, 'rooms/room_list.html', context)


@login_required
@receptionist_or_above
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    from guests.models import GuestStay
    from requests_app.models import ServiceRequest

    current_stay    = GuestStay.objects.filter(room=room, is_active=True).select_related('guest').first()
    recent_requests = ServiceRequest.objects.filter(room=room).order_by('-created_at')[:10]

    context = {
        'room':             room,
        'current_stay':     current_stay,
        'recent_requests':  recent_requests,
    }
    return render(request, 'rooms/room_detail.html', context)


@login_required
@manager_required
def room_create(request):
    from .forms import RoomForm
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f"Room {room.number} created.")
            return redirect('rooms:room_detail', pk=room.pk)
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Add Room'})


@login_required
@manager_required
def room_edit(request, pk):
    from .forms import RoomForm
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f"Room {room.number} updated.")
            return redirect('rooms:room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form, 'title': f'Edit Room {room.number}'})


@login_required
def room_qr(request, pk):
    """Shows the printable QR code page for a room."""
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'rooms/room_qr.html', {'room': room})


@login_required
def update_room_status(request, pk):
    """Quick status update from the room list."""
    if request.method == 'POST':
        room = get_object_or_404(Room, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(RoomStatus.choices):
            room.status = new_status
            room.save()
            messages.success(request, f"Room {room.number} status updated to {room.get_status_display()}.")
    return redirect('rooms:room_list')
