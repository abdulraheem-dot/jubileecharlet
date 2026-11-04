"""
integrations/signals.py

Watches Booking status transitions and pushes them to the management system.

A booking moves to CONFIRMED after a successful payment (see
payments/views.py::_mark_payment_success) and to CANCELLED when an admin
approves a cancellation request.  We catch those transitions regardless of
which code path caused them, and run the sync AFTER the transaction commits so
we never hold a DB lock during the outbound HTTP call.
"""

import logging

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from bookings.models import Booking
from .services import sync_booking_to_pms, cancel_booking_in_pms

logger = logging.getLogger('jubilee')


@receiver(pre_save, sender=Booking)
def _stash_previous_status(sender, instance, **kwargs):
    """Remember the booking's status before this save so post_save can detect transitions."""
    if instance.pk:
        instance._previous_status = (
            Booking.objects.filter(pk=instance.pk)
            .values_list('status', flat=True)
            .first()
        )
    else:
        instance._previous_status = None


@receiver(post_save, sender=Booking)
def _sync_on_status_change(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_status', None)
    current = instance.status

    if current == 'confirmed' and previous != 'confirmed':
        transaction.on_commit(lambda: sync_booking_to_pms(instance))
    elif current == 'cancelled' and previous != 'cancelled':
        transaction.on_commit(lambda: cancel_booking_in_pms(instance))
