from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPES = [
        ('NEW_REQUEST',  'New Request'),
        ('ASSIGNMENT',   'Assignment'),
        ('STATUS_CHANGE','Status Change'),
        ('GUEST_MESSAGE','Guest Message'),
        ('COMPLETION',   'Completion'),
        ('URGENT',       'Urgent Alert'),
        ('ESCALATION',   'Escalation'),
        ('LOW_STOCK',    'Low Stock'),
        ('GENERAL',      'General'),
    ]

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title            = models.CharField(max_length=200)
    message          = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default='GENERAL')

    # Optional link to the related request
    related_request  = models.ForeignKey(
        'requests_app.ServiceRequest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications'
    )

    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.recipient.get_full_name()}] {self.title}"

    class Meta:
        ordering = ['-created_at']
