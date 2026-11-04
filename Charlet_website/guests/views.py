"""
guests/views.py

Two sides of the guests app:
1. Staff views — manage guest profiles and check-ins
2. Guest portal views — what guests see when they scan their QR code
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import Guest, GuestStay
from rooms.models import Room, RoomStatus
from accounts.decorators import receptionist_or_above
from .forms import GuestForm, GuestStayForm, GuestPortalLoginForm

User = get_user_model()


# ===========================================================================
# STAFF VIEWS
# ===========================================================================

@login_required
@receptionist_or_above
def guest_list(request):
    """List all guests — active and historical."""
    guests = Guest.objects.select_related('user').prefetch_related('stays__room')

    # Filter to only active (currently checked in) guests
    active_only = request.GET.get('active', '')
    if active_only:
        guests = guests.filter(stays__is_active=True).distinct()

    search = request.GET.get('q', '')
    if search:
        guests = guests.filter(
            first_name__icontains=search
        ) | guests.filter(
            last_name__icontains=search
        ) | guests.filter(
            email__icontains=search
        )

    context = {
        'guests':      guests.order_by('-created_at'),
        'active_only': active_only,
        'search':      search,
        'total':       guests.count(),
    }
    return render(request, 'guests/guest_list.html', context)


@login_required
@receptionist_or_above
def guest_detail(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    stays = guest.stays.select_related('room', 'checked_in_by').order_by('-check_in_date')
    current_stay = stays.filter(is_active=True).first()

    from requests_app.models import ServiceRequest
    requests = ServiceRequest.objects.filter(guest=guest).order_by('-created_at')[:20]

    context = {
        'guest':        guest,
        'stays':        stays,
        'current_stay': current_stay,
        'requests':     requests,
    }
    return render(request, 'guests/guest_detail.html', context)


@login_required
@receptionist_or_above
def guest_checkin(request):
    """Check in a new or returning guest."""
    if request.method == 'POST':
        guest_form = GuestForm(request.POST)
        stay_form  = GuestStayForm(request.POST)

        if guest_form.is_valid() and stay_form.is_valid():
            with transaction.atomic():
                # transaction.atomic() ensures both saves happen together.
                # If either fails, neither is saved — keeps data consistent.
                guest = guest_form.save()

                stay       = stay_form.save(commit=False)
                stay.guest = guest
                stay.checked_in_by = request.user

                room = stay.room
                if room.status not in [RoomStatus.AVAILABLE, RoomStatus.RESERVED]:
                    messages.error(request, f"Room {room.number} is not available for check-in.")
                    return redirect('guests:guest_checkin')

                # Create a guest portal user account if email provided
                if guest.email:
                    portal_user, created = User.objects.get_or_create(
                        email=guest.email,
                        defaults={
                            'username':      f"guest_{guest.email.split('@')[0]}_{guest.pk}",
                            'first_name':    guest.first_name,
                            'last_name':     guest.last_name,
                            'is_guest_user': True,
                        }
                    )
                    if created:
                        portal_user.set_password(room.access_token[:8])
                        portal_user.save()
                    guest.user = portal_user
                    guest.save()

                stay.save()

                # Update room status to OCCUPIED
                room.status = RoomStatus.OCCUPIED
                room.save()

            messages.success(request, f"{guest.get_full_name()} checked in to Room {room.number}.")
            return redirect('guests:guest_detail', pk=guest.pk)
    else:
        guest_form = GuestForm()
        stay_form  = GuestStayForm()

    available_rooms = Room.objects.filter(
        status__in=[RoomStatus.AVAILABLE, RoomStatus.RESERVED]
    ).select_related('room_type')

    return render(request, 'guests/guest_checkin.html', {
        'guest_form':       guest_form,
        'stay_form':        stay_form,
        'available_rooms':  available_rooms,
    })


@login_required
@receptionist_or_above
def guest_checkout(request, pk):
    stay = get_object_or_404(GuestStay, pk=pk, is_active=True)
    if request.method == 'POST':
        stay.checkout(staff_user=request.user)
        messages.success(request, f"{stay.guest.get_full_name()} checked out from Room {stay.room.number}.")
        return redirect('guests:guest_detail', pk=stay.guest.pk)

    return render(request, 'guests/guest_checkout_confirm.html', {'stay': stay})


# ===========================================================================
# GUEST PORTAL VIEWS
# ===========================================================================

def portal_entry(request):
    """
    The guest portal landing page.
    Guests arrive here after scanning their room QR code or manually navigating.
    Shows login form or links to room-specific access.

    POST: validate room number + access code, set session, redirect to portal home.
    GET:  just render the form.
    """
    form = GuestPortalLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        room_number = form.cleaned_data['room_number']
        access_code = form.cleaned_data['access_code']

        # Look up the room by its number
        room = Room.objects.filter(number=room_number).first()

        # Validate: room must exist, be occupied, and the access code must match
        if room and room.access_token and room.access_token.startswith(access_code):
            current_stay = GuestStay.objects.filter(room=room, is_active=True).first()
            if current_stay:
                # Store room info in session (same as QR scan flow)
                request.session['guest_room_token'] = room.access_token
                request.session['guest_room_id']    = room.pk
                request.session['guest_stay_id']    = current_stay.pk
                return redirect('guests:portal_home')
            else:
                messages.error(request, "No active stay found for that room. Please check with reception.")
        else:
            messages.error(request, "Invalid room number or access code. Please try again.")

    return render(request, 'guests/portal_entry.html', {'form': form})


def portal_room_access(request, token):
    """
    Called when a guest scans their room QR code.
    The token in the URL is the room's unique access_token.
    We look up the room and start a session for that room.
    This means the guest doesn't need a username/password —
    the QR code IS their authentication for basic service requests.
    """
    room = get_object_or_404(Room, access_token=token)
    current_stay = GuestStay.objects.filter(room=room, is_active=True).select_related('guest').first()

    if not current_stay:
        return render(request, 'guests/portal_no_checkin.html', {'room': room})

    # Store room token in session so portal views know which room this is
    request.session['guest_room_token'] = token
    request.session['guest_room_id']    = room.pk
    request.session['guest_stay_id']    = current_stay.pk

    return redirect('guests:portal_home')


def portal_logout(request):
    """
    Signs the guest out of the portal.
    Clears all guest session variables and redirects to the entry page.
    Works for both session-based (QR scan) and auth-based access.
    """
    # Flush the entire session — clears all guest_room_* keys
    for key in ('guest_room_token', 'guest_room_id', 'guest_stay_id'):
        request.session.pop(key, None)

    # If the guest was authenticated via Django auth, log them out too
    if request.user.is_authenticated and request.user.is_guest_user:
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)

    messages.info(request, "You have been signed out of the guest portal.")
    return redirect('guests:portal_entry')


def portal_home(request):
    """
    The main guest portal home page — shown after QR scan.
    Big service buttons, current requests, messaging.
    """
    # Check for session-based room access (QR scan) or logged-in guest
    room    = None
    stay    = None
    guest   = None

    if request.user.is_authenticated and request.user.is_guest_user:
        try:
            guest = request.user.guest_profile
            stay  = guest.current_stay
            room  = stay.room if stay else None
        except Exception:
            pass
    else:
        # Session-based access from QR scan
        room_id  = request.session.get('guest_room_id')
        stay_id  = request.session.get('guest_stay_id')
        if room_id and stay_id:
            room = Room.objects.filter(pk=room_id).select_related('room_type').first()
            stay = GuestStay.objects.filter(pk=stay_id, is_active=True).select_related('guest').first()
            if stay:
                guest = stay.guest

    if not room:
        return redirect('guests:portal_entry')

    # Security check: if the guest has a linked user account that has been
    # deactivated by an admin, kick them out immediately.
    if guest and guest.user_id:
        from django.contrib.auth import get_user_model
        linked_user = get_user_model().objects.filter(pk=guest.user_id).first()
        if linked_user and not linked_user.is_active:
            # Clear the session and send them back to the entry page
            for key in ('guest_room_token', 'guest_room_id', 'guest_stay_id'):
                request.session.pop(key, None)
            messages.error(request, "Your portal access has been revoked. Please contact reception.")
            return redirect('guests:portal_entry')

    from requests_app.models import ServiceRequest
    active_requests = ServiceRequest.objects.filter(
        room=room, guest=guest
    ).exclude(status='COMPLETED').order_by('-created_at') if guest else []

    context = {
        'room':            room,
        'stay':            stay,
        'guest':           guest,
        'active_requests': active_requests,
    }
    return render(request, 'guests/portal_home.html', context)
