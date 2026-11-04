from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Feedback(models.Model):
    request     = models.OneToOneField(
        'requests_app.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    guest       = models.ForeignKey('guests.Guest', on_delete=models.CASCADE, related_name='feedback')
    rating      = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment     = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for #{self.request.request_number} — {self.rating}★"

    class Meta:
        ordering = ['-created_at']


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN       = 'OPEN',       'Open'
        IN_REVIEW  = 'IN_REVIEW',  'In Review'
        RESOLVED   = 'RESOLVED',   'Resolved'
        CLOSED     = 'CLOSED',     'Closed'

    class Category(models.TextChoices):
        SERVICE    = 'SERVICE',    'Service Quality'
        CLEANLINESS= 'CLEANLINESS','Room Cleanliness'
        FACILITIES = 'FACILITIES', 'Facilities'
        STAFF      = 'STAFF',      'Staff Behaviour'
        FOOD       = 'FOOD',       'Food Quality'
        NOISE      = 'NOISE',      'Noise'
        OTHER      = 'OTHER',      'Other'

    guest       = models.ForeignKey('guests.Guest', on_delete=models.CASCADE, related_name='complaints')
    room        = models.ForeignKey('rooms.Room', on_delete=models.CASCADE)
    category    = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField()
    priority    = models.CharField(
        max_length=10,
        choices=[('LOW','Low'),('NORMAL','Normal'),('HIGH','High'),('URGENT','Urgent')],
        default='NORMAL'
    )
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    resolution  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Complaint #{self.pk} — Room {self.room.number} ({self.status})"

    class Meta:
        ordering = ['-created_at']
