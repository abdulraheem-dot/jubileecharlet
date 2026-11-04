"""
integrations/views.py

Receives booking data from the public website and exposes room availability
back to it.

Endpoints (all require X-API-Key):
    POST /integrations/api/sync-booking/      — create/update a Reservation
    POST /integrations/api/cancel-booking/   — cancel a Reservation
    GET  /integrations/api/room-availability/ — room-type availability for dates

ROOM MAPPING
------------
The website's ``accommodation.Room`` (a priced, bookable listing) maps to our
``rooms.RoomType`` (a priced category).  We match by slugified name so the two
systems don't need to share IDs.  If no match is found the reservation is still
created with a null room_type — reception can fix it up at check-in.
"""

import json
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.utils.text import slugify
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from .decorators import require_api_key
from .models import Reservation, SyncLog


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _log(endpoint, external_reference, result, message, payload):
    SyncLog.objects.create(
        endpoint=endpoint,
        external_reference=external_reference,
        result=result,
        message=message,
        payload=payload,
    )


def match_room_type(name):
    """Find a RoomType whose name matches the website room name (slug-insensitive)."""
    from rooms.models import RoomType
    if not name:
        return None
    # Fast path: exact (case-insensitive) name match
    rt = RoomType.objects.filter(name__iexact=name).first()
    if rt:
        return rt
    # Fallback: compare slugified names so "Deluxe Room" == "deluxe-room"
    target = slugify(name)
    for rt in RoomType.objects.all():
        if slugify(rt.name) == target:
            return rt
    return None


def _get_or_create_guest(guest_data):
    """Find an existing Guest by email, or create one.  Updates blanks too."""
    from guests.models import Guest
    email = (guest_data.get('email') or '').strip()
    first_name = (guest_data.get('first_name') or '').strip()
    last_name = (guest_data.get('last_name') or '').strip()
    phone = guest_data.get('phone_number') or ''

    guest = None
    if email:
        guest = Guest.objects.filter(email__iexact=email).first()

    if guest is None:
        guest = Guest.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone,
        )
    else:
        # Fill in any missing details so we learn more about returning guests
        changed = False
        if not guest.first_name and first_name:
            guest.first_name = first_name
            changed = True
        if not guest.last_name and last_name:
            guest.last_name = last_name
            changed = True
        if not guest.phone_number and phone:
            guest.phone_number = phone
            changed = True
        if changed:
            guest.save()
    return guest


def _parse_amount(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0.00')


# ---------------------------------------------------------------------------
# POST /sync-booking/
# ---------------------------------------------------------------------------
@csrf_exempt
@require_api_key
def sync_booking(request):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        _log('sync-booking', '', SyncLog.Result.FAILED, 'Invalid JSON', {})
        return JsonResponse({'message': 'Invalid JSON.'}, status=400)

    ext_ref = (data.get('external_reference') or '').strip()
    if not ext_ref:
        _log('sync-booking', '', SyncLog.Result.FAILED, 'Missing external_reference', data)
        return JsonResponse({'message': 'external_reference is required.'}, status=400)

    guest_data = data.get('guest') or {}
    if not guest_data.get('email'):
        _log('sync-booking', ext_ref, SyncLog.Result.FAILED, 'Missing guest email', data)
        return JsonResponse({'message': 'guest.email is required.'}, status=400)

    try:
        guest = _get_or_create_guest(guest_data)
    except Exception as exc:  # noqa: BLE001 — log and report cleanly
        _log('sync-booking', ext_ref, SyncLog.Result.FAILED, f'Guest error: {exc}', data)
        return JsonResponse({'message': 'Could not create/update guest.'}, status=400)

    # Map website rooms → room types
    rooms_data = data.get('rooms') or []
    room_details = []
    first_type = None
    for r in rooms_data:
        rt = match_room_type(r.get('name'))
        room_details.append({
            'name': r.get('name'),
            'price_per_night': r.get('price_per_night'),
            'room_type': rt.name if rt else None,
        })
        if rt and first_type is None:
            first_type = rt

    check_in = parse_date(data.get('check_in_date') or '')
    check_out = parse_date(data.get('check_out_date') or '')
    if not check_in or not check_out:
        _log('sync-booking', ext_ref, SyncLog.Result.FAILED, 'Missing/invalid dates', data)
        return JsonResponse({'message': 'Valid check_in_date and check_out_date are required.'}, status=400)

    incoming_status = data.get('status') or Reservation.Status.CONFIRMED

    try:
        reservation = Reservation.objects.filter(external_reference=ext_ref).first()
        created = reservation is None

        if created:
            reservation = Reservation(
                external_reference=ext_ref,
                status=incoming_status,
            )

        # Update the mutable fields
        reservation.guest = guest
        reservation.room_type = first_type
        reservation.room_details = room_details
        reservation.check_in_date = check_in
        reservation.check_out_date = check_out
        reservation.num_adults = data.get('num_adults', 1) or 1
        reservation.num_children = data.get('num_children', 0) or 0
        reservation.total_amount = _parse_amount(data.get('total_amount'))
        reservation.special_requests = data.get('special_requests') or ''

        # Don't clobber operational statuses: once a guest has been checked in
        # or out by staff here, a re-sync from the website shouldn't rewind it.
        if not created and reservation.status not in (
            Reservation.Status.CHECKED_IN,
            Reservation.Status.CHECKED_OUT,
        ):
            reservation.status = incoming_status

        reservation.save()

        _log('sync-booking', ext_ref, SyncLog.Result.SUCCESS,
             f"{'Created' if created else 'Updated'} reservation for {guest}", data)
        return JsonResponse(
            {'status': 'ok', 'reservation_id': reservation.pk, 'created': created},
            status=201 if created else 200,
        )
    except Exception as exc:  # noqa: BLE001
        _log('sync-booking', ext_ref, SyncLog.Result.FAILED, f'Error: {exc}', data)
        return JsonResponse({'message': 'Could not save reservation.'}, status=500)


# ---------------------------------------------------------------------------
# POST /cancel-booking/
# ---------------------------------------------------------------------------
@csrf_exempt
@require_api_key
def cancel_booking(request):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        _log('cancel-booking', '', SyncLog.Result.FAILED, 'Invalid JSON', {})
        return JsonResponse({'message': 'Invalid JSON.'}, status=400)

    ext_ref = (data.get('external_reference') or '').strip()
    if not ext_ref:
        return JsonResponse({'message': 'external_reference is required.'}, status=400)

    try:
        reservation = Reservation.objects.filter(external_reference=ext_ref).first()
        if reservation is None:
            _log('cancel-booking', ext_ref, SyncLog.Result.SUCCESS, 'No matching reservation (idempotent)', data)
            return JsonResponse({'status': 'ok', 'message': 'No matching reservation.'})

        # Don't touch a stay that's already in progress
        if reservation.status in (Reservation.Status.CHECKED_IN, Reservation.Status.CHECKED_OUT):
            _log('cancel-booking', ext_ref, SyncLog.Result.FAILED,
                 f"Cannot cancel — already {reservation.get_status_display()}", data)
            return JsonResponse(
                {'message': f"Cannot cancel — guest already {reservation.get_status_display().lower()}."},
                status=409,
            )

        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        _log('cancel-booking', ext_ref, SyncLog.Result.SUCCESS, 'Cancelled', data)
        return JsonResponse({'status': 'ok', 'reservation_id': reservation.pk})
    except Exception as exc:  # noqa: BLE001
        _log('cancel-booking', ext_ref, SyncLog.Result.FAILED, f'Error: {exc}', data)
        return JsonResponse({'message': 'Could not cancel reservation.'}, status=500)


# ---------------------------------------------------------------------------
# GET /room-availability/?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD
# ---------------------------------------------------------------------------
@csrf_exempt
@require_api_key
def room_availability(request):
    """
    Report, per room type, how many physical rooms are bookable.

    A room type is ``bookable`` when the number of physically-available rooms
    (status == AVAILABLE) exceeds the number of reservations already held for
    the requested dates.  Keys are slugified room-type names so the website can
    look them up by its room listing slug.
    """
    from rooms.models import RoomType, Room, RoomStatus

    check_in = parse_date(request.GET.get('check_in', ''))
    check_out = parse_date(request.GET.get('check_out', ''))

    room_types_out = {}
    for rt in RoomType.objects.all():
        total = Room.objects.filter(room_type=rt).count()
        available_physical = Room.objects.filter(
            room_type=rt, status=RoomStatus.AVAILABLE
        ).count()

        reserved = 0
        if check_in and check_out:
            reserved = Reservation.objects.filter(
                room_type=rt,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
                status__in=[
                    Reservation.Status.PENDING,
                    Reservation.Status.CONFIRMED,
                    Reservation.Status.CHECKED_IN,
                ],
            ).count()

        free = available_physical - reserved
        room_types_out[slugify(rt.name)] = {
            'name': rt.name,
            'total': total,
            'available': max(free, 0),
            'bookable': free > 0,
        }

    return JsonResponse({
        'check_in': str(check_in) if check_in else None,
        'check_out': str(check_out) if check_out else None,
        'room_types': room_types_out,
    })
