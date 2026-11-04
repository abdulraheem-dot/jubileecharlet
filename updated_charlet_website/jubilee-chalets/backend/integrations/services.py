"""
integrations/services.py

High-level operations against the management system (PMS).

    sync_booking_to_pms(booking)          — push a confirmed booking inward
    cancel_booking_in_pms(booking)         — tell the PMS a booking is cancelled
    get_pms_unavailable_rooms(rooms, ...)  — rooms the PMS says aren't bookable

Every function degrades gracefully: if the PMS isn't configured or is
unreachable, it logs and returns a safe default (None / empty list) so the
booking site never breaks because the management system is down.
"""

import logging

from django.conf import settings
from django.utils.text import slugify

from .client import PMSClient, PMSNotConfigured

logger = logging.getLogger('jubilee')


def pms_room_type_name(room):
    """
    Return the PMS room-type name a website room maps to.

    By default a website room maps to the PMS room type with the same
    slugified name (e.g. "Deluxe Room" → "deluxe-room").  If the two systems
    use different names, set ``PMS_ROOM_TYPE_MAP`` in settings to
    ``{website_room_slug: pms_room_type_name}`` to override it per room, e.g.::

        PMS_ROOM_TYPE_MAP = {"deluxe-king": "Deluxe Room"}
    """
    mapping = getattr(settings, 'PMS_ROOM_TYPE_MAP', {}) or {}
    return mapping.get(slugify(room.name)) or room.name


def sync_booking_to_pms(booking):
    """Push a booking (with its guest and rooms) to the management system."""
    client = PMSClient()
    if not client.configured:
        logger.debug('PMS not configured — skipping sync for %s', booking.booking_reference)
        return None

    rooms = []
    for br in booking.booking_rooms.select_related('room'):
        rooms.append({
            # Send the canonical PMS room-type name so the PMS can match it,
            # even when the website room name differs (see PMS_ROOM_TYPE_MAP).
            'name': pms_room_type_name(br.room),
            'price_per_night': str(br.price_per_night),
        })

    guest = booking.guest
    payload = {
        'external_reference': booking.booking_reference,
        'guest': {
            'first_name': guest.first_name,
            'last_name': guest.last_name,
            'email': guest.email,
            'phone_number': guest.phone_number or '',
        },
        'check_in_date': str(booking.check_in_date),
        'check_out_date': str(booking.check_out_date),
        'num_adults': booking.num_adults,
        'num_children': booking.num_children,
        'total_amount': str(booking.total_amount),
        'special_requests': booking.special_requests or '',
        'rooms': rooms,
        'status': 'CONFIRMED',
    }

    try:
        result = client.sync_booking(payload)
        logger.info('PMS sync OK for %s → %s', booking.booking_reference, result)
        return result
    except PMSNotConfigured:
        return None
    except Exception as exc:  # noqa: BLE001 — network/HTTP errors must not break booking
        logger.exception('PMS sync failed for %s: %s', booking.booking_reference, exc)
        return None


def cancel_booking_in_pms(booking):
    """Notify the management system that a booking was cancelled."""
    client = PMSClient()
    if not client.configured:
        return None
    try:
        result = client.cancel_booking(booking.booking_reference)
        logger.info('PMS cancel OK for %s → %s', booking.booking_reference, result)
        return result
    except PMSNotConfigured:
        return None
    except Exception as exc:  # noqa: BLE001
        logger.exception('PMS cancel failed for %s: %s', booking.booking_reference, exc)
        return None


def get_pms_unavailable_rooms(rooms, check_in, check_out):
    """
    Return the names of rooms the PMS says are NOT bookable for the dates.

    The PMS is the source of truth for physical room status (maintenance,
    out-of-service, occupied by walk-ins).  We ask it for per-room-type
    availability and match each website room to its room type by slug.

    Returns an empty list when the PMS isn't configured or is unreachable,
    so callers can treat "no answer" as "don't block" (graceful fallback).
    """
    client = PMSClient()
    if not client.configured:
        return []

    try:
        data = client.get_room_availability(str(check_in), str(check_out))
    except PMSNotConfigured:
        return []
    except Exception as exc:  # noqa: BLE001
        logger.warning('PMS availability check failed — falling back to local checks: %s', exc)
        return []

    room_types = data.get('room_types', {})
    unavailable = []
    for room in rooms:
        # Match the website room to a PMS room type, honouring PMS_ROOM_TYPE_MAP
        info = room_types.get(slugify(pms_room_type_name(room)))
        if info is not None and not info.get('bookable', True):
            unavailable.append(room.name)
    return unavailable
