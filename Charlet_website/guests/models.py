"""
guests/models.py

Guest profile and stay models.

KEY CONCEPTS:
- GuestStay is the bridge between a Guest and a Room for a specific visit.
- A guest can have many stays over time (return visitors).
- Only one stay per room can be active at a time (enforced in save()).
- Guests can have a User account (for the portal) or be walk-in (no account).
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Guest(models.Model):
    """
    Stores personal information about a hotel guest.

    OneToOneField to User (optional — blank=True, null=True):
    Walk-in guests may not have a portal account.
    When a guest is given portal access, we link their User account here.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='guest_profile',
        help_text="Portal account for this guest (optional)"
    )

    # Personal details
    first_name   = models.CharField(max_length=100)
    last_name    = models.CharField(max_length=100)
    email        = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    nationality  = models.CharField(max_length=100, blank=True)
    id_type      = models.CharField(
        max_length=30, blank=True,
        help_text="e.g. National ID, Passport, Driver's Licence"
    )
    id_number    = models.CharField(max_length=50, blank=True)

    # Guest preferences (for future personalisation)
    special_requirements = models.TextField(
        blank=True,
        help_text="Dietary needs, accessibility, allergies, etc."
    )

    # VIP status
    is_vip = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def current_stay(self):
        """Returns the guest's active (current) stay, or None."""
        return self.stays.filter(is_active=True).select_related('room').first()

    @property
    def current_room(self):
        stay = self.current_stay
        return stay.room if stay else None

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'


class GuestStay(models.Model):
    """
    Records a single check-in/check-out period for a guest.

    WHY A SEPARATE MODEL?
    Because a guest may visit the hotel multiple times.
    Each visit is a separate 'stay' linked to both the guest and the room.

    BUSINESS RULES:
    - is_active=True means the guest is currently in the hotel.
    - When checking out, set is_active=False and actual_checkout=now.
    - Only one active stay per room at a time.
    """
    guest           = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='stays')
    room            = models.ForeignKey('rooms.Room', on_delete=models.PROTECT, related_name='stays')
    checked_in_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='checked_in_guests'
    )
    checked_out_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='checked_out_guests'
    )

    check_in_date   = models.DateTimeField(default=timezone.now)
    expected_checkout = models.DateField(null=True, blank=True)
    actual_checkout   = models.DateTimeField(null=True, blank=True)

    number_of_guests  = models.PositiveIntegerField(default=1)
    is_active         = models.BooleanField(default=True)

    # Staff notes about this stay
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest} — Room {self.room.number} ({'Active' if self.is_active else 'Checked Out'})"

    def checkout(self, staff_user=None):
        """
        Performs the check-out action:
        - Sets is_active=False
        - Records the checkout time and staff member
        - Updates the room status back to AVAILABLE
        """
        from rooms.models import RoomStatus
        self.is_active       = False
        self.actual_checkout = timezone.now()
        if staff_user:
            self.checked_out_by = staff_user
        self.save()

        # Update room status
        self.room.status = RoomStatus.AVAILABLE
        self.room.save()

    @property
    def nights_stayed(self):
        end = self.actual_checkout or timezone.now()
        delta = end - self.check_in_date
        return max(delta.days, 1)

    class Meta:
        ordering = ['-check_in_date']
        verbose_name = 'Guest Stay'
        verbose_name_plural = 'Guest Stays'
