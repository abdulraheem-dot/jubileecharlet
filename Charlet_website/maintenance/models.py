from django.db import models
from django.conf import settings


class MaintenanceCategory(models.TextChoices):
    AC          = 'AC',          'Air Conditioning'
    PLUMBING    = 'PLUMBING',    'Plumbing'
    ELECTRICITY = 'ELECTRICITY', 'Electricity'
    TELEVISION  = 'TELEVISION',  'Television'
    INTERNET    = 'INTERNET',    'Internet / WiFi'
    LIGHTING    = 'LIGHTING',    'Lighting'
    FURNITURE   = 'FURNITURE',   'Furniture'
    BATHROOM    = 'BATHROOM',    'Bathroom'
    OTHER       = 'OTHER',       'Other'


class MaintenanceRecord(models.Model):
    class Status(models.TextChoices):
        OPEN        = 'OPEN',        'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD     = 'ON_HOLD',     'On Hold'
        COMPLETED   = 'COMPLETED',   'Completed'
        CANCELLED   = 'CANCELLED',   'Cancelled'

    room        = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='maintenance_records')
    category    = models.CharField(max_length=20, choices=MaintenanceCategory.choices)
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority    = models.CharField(
        max_length=10,
        choices=[('LOW','Low'),('NORMAL','Normal'),('HIGH','High'),('URGENT','Urgent')],
        default='NORMAL'
    )
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reported_maintenance'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_maintenance'
    )

    notes       = models.TextField(blank=True, help_text="Technician notes")
    photo       = models.ImageField(upload_to='maintenance_photos/', blank=True, null=True)
    photo_after = models.ImageField(upload_to='maintenance_photos/', blank=True, null=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.get_category_display()}] Room {self.room.number} — {self.title}"

    class Meta:
        ordering = ['-created_at']
