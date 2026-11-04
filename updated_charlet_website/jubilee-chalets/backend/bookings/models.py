import uuid
from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def generate_booking_reference():
    """Generate a unique 8-char uppercase reference like JC-A3B2C1D4"""
    return f"JC-{uuid.uuid4().hex[:8].upper()}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        AWAITING_PAYMENT = 'awaiting_payment', 'Awaiting Payment'
        CONFIRMED = 'confirmed', 'Confirmed'
        CHECKED_IN = 'checked_in', 'Checked In'
        CHECKED_OUT = 'checked_out', 'Checked Out'
        CANCELLATION_REQUESTED = 'cancellation_requested', 'Cancellation Requested'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PARTIAL = 'partial', 'Partial'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Failed'

    booking_reference = models.CharField(max_length=20, unique=True, default=generate_booking_reference, editable=False)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    special_requests = models.TextField(blank=True)

    # Financials — always calculated server-side
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    taxes_fees = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['guest', 'status']),
            models.Index(fields=['check_in_date', 'check_out_date']),
        ]

    def __str__(self):
        return f'{self.booking_reference} — {self.guest.email}'

    def clean(self):
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValidationError('Check-out must be after check-in.')
            if self.check_in_date < timezone.now().date() and not self.pk:
                raise ValidationError('Check-in date cannot be in the past.')

    @property
    def num_nights(self):
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0

    def calculate_totals(self):
        """Recalculate subtotal and total from room allocations."""
        self.subtotal = sum(br.total_price for br in self.booking_rooms.all())
        self.taxes_fees = Decimal('0.00')
        self.total_amount = self.subtotal + self.taxes_fees
        return self.total_amount


class BookingRoom(models.Model):
    """Links a booking to a specific room with locked-in pricing."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_rooms')
    room = models.ForeignKey('accommodation.Room', on_delete=models.PROTECT, related_name='booking_rooms')
    price_per_night = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        unique_together = [('booking', 'room')]

    def __str__(self):
        return f'{self.booking.booking_reference} — {self.room.name}'

    def save(self, *args, **kwargs):
        # Lock in pricing and calculate total from server-side data only
        if not self.price_per_night:
            self.price_per_night = self.room.price_per_night
        self.total_price = self.price_per_night * self.booking.num_nights
        super().save(*args, **kwargs)


class CancellationRequest(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation_request')
    reason = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_cancellations'
    )
    is_approved = models.BooleanField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    def __str__(self):
        return f'Cancellation: {self.booking.booking_reference}'
