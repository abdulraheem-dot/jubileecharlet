"""
integrations/models.py

Models that bridge the public booking website (the "outer" site) with this
internal hotel management system (the "inner" site).

WHY THESE MODELS EXIST
----------------------
The public website takes online reservations and payments.  Staff here need
to *see* those reservations so reception can check guests in, housekeeping can
prepare rooms, and management can report on occupancy.

We do NOT reuse ``guests.GuestStay`` for online bookings.  ``GuestStay`` records
a guest who is *physically* in a room right now (actual check-in at the front
desk).  An online booking is a *reservation* for a future stay — it has no
physical room assigned until the guest arrives.  Keeping them separate keeps
both concepts clean:

    Online booking  ──►  Reservation  ──(check-in at desk)──►  GuestStay

So:
    Reservation  = "someone booked online, they're coming on these dates"
    GuestStay    = "that same someone has now physically arrived and is in room 101"

A ``Reservation`` can be converted into a ``GuestStay`` via ``check_in()``.
"""

from decimal import Decimal
from django.db import models
from django.utils import timezone


class Reservation(models.Model):
    """
    An online reservation pushed from the public booking website.

    The ``external_reference`` is the booking reference generated on the
    website (e.g. ``JC-A3B2C1D4``).  It is unique and is used to make the sync
    idempotent — re-sending the same booking simply updates the record.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CHECKED_IN = 'CHECKED_IN', 'Checked In'
        CHECKED_OUT = 'CHECKED_OUT', 'Checked Out'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class Source(models.TextChoices):
        WEBSITE = 'WEBSITE', 'Website'

    # Who is coming
    guest = models.ForeignKey(
        'guests.Guest',
        on_delete=models.PROTECT,
        related_name='reservations',
        help_text="The hotel guest record for this booking",
    )

    # What they booked (room *type*, not a specific physical room — that is
    # assigned at check-in).  Nullable so a booking is never rejected just
    # because a matching room type hasn't been set up here yet.
    room_type = models.ForeignKey(
        'rooms.RoomType',
        on_delete=models.PROTECT,
        related_name='reservations',
        null=True, blank=True,
        help_text="Room type matched from the website room name (assigned at check-in)",
    )
    assigned_room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.SET_NULL,
        related_name='reservations',
        null=True, blank=True,
        help_text="Physical room assigned when the guest checks in",
    )

    # The full list of rooms/types as sent by the website, stored verbatim so
    # nothing is lost even if the room-type mapping isn't perfect.
    room_details = models.JSONField(
        default=list, blank=True,
        help_text="Raw list of rooms booked on the website [{name, price_per_night, room_type}]",
    )

    # When
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)

    # Money
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    special_requests = models.TextField(blank=True)

    # Link back to the website
    external_reference = models.CharField(
        max_length=30, unique=True, db_index=True,
        help_text="Booking reference from the website (e.g. JC-A3B2C1D4)",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEBSITE)

    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.external_reference} — {self.guest} ({self.get_status_display()})"

    @property
    def num_nights(self):
        if self.check_in_date and self.check_out_date and self.check_out_date > self.check_in_date:
            return (self.check_out_date - self.check_in_date).days
        return 0

    def check_in(self, room, staff_user=None):
        """
        Convert this reservation into an actual stay.

        Creates a ``GuestStay`` (the existing check-in model), assigns the
        physical room, marks the room as occupied, and updates this reservation
        to ``CHECKED_IN``.  Returns the created ``GuestStay``.
        """
        from guests.models import GuestStay
        from rooms.models import RoomStatus

        stay = GuestStay.objects.create(
            guest=self.guest,
            room=room,
            checked_in_by=staff_user,
            check_in_date=timezone.now(),
            expected_checkout=self.check_out_date,
            number_of_guests=self.num_adults + self.num_children,
            is_active=True,
            notes=f"From online reservation {self.external_reference}",
        )

        self.assigned_room = room
        self.status = self.Status.CHECKED_IN
        self.save()

        room.status = RoomStatus.OCCUPIED
        room.save()
        return stay

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'


class SyncLog(models.Model):
    """Audit trail of every request received from the website."""

    class Result(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    endpoint = models.CharField(max_length=50)
    external_reference = models.CharField(max_length=30, blank=True)
    result = models.CharField(max_length=10, choices=Result.choices)
    message = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.endpoint} — {self.result} ({self.created_at:%Y-%m-%d %H:%M})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sync Log'
        verbose_name_plural = 'Sync Logs'
