from django.db import models
from django.conf import settings


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        ABANDONED = 'abandoned', 'Abandoned'
        REFUNDED = 'refunded', 'Refunded'

    booking = models.ForeignKey('bookings.Booking', on_delete=models.PROTECT, related_name='payments')
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    channel = models.CharField(max_length=50, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    paystack_id = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Idempotency — track webhook events we've already processed
    webhook_events_processed = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['reference']), models.Index(fields=['status'])]

    def __str__(self):
        return f'Payment {self.reference} — {self.status}'
