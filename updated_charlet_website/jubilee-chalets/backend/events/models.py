from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField


class EventVenue(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.PositiveIntegerField(null=True, blank=True)
    amenities = models.TextField(blank=True, help_text='Comma-separated list of amenities')
    images = JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class EventEnquiry(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_REVIEW = 'in_review', 'In Review'
        QUOTED = 'quoted', 'Quoted'
        CONFIRMED = 'confirmed', 'Confirmed'
        REJECTED = 'rejected', 'Rejected'
        CLOSED = 'closed', 'Closed'

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    event_type = models.CharField(max_length=100)
    event_date = models.DateField()
    expected_attendees = models.PositiveIntegerField()
    venue = models.ForeignKey(EventVenue, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    catering_required = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Event Enquiries'

    def __str__(self):
        return f'{self.event_type} — {self.full_name} ({self.event_date})'
