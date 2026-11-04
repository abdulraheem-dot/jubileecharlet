from django.db import models
from django.conf import settings


class HousekeepingTask(models.Model):
    class TaskType(models.TextChoices):
        DAILY_CLEAN   = 'DAILY_CLEAN',   'Daily Cleaning'
        TURNDOWN      = 'TURNDOWN',      'Turndown Service'
        DEEP_CLEAN    = 'DEEP_CLEAN',    'Deep Clean'
        CHECKOUT_CLEAN= 'CHECKOUT_CLEAN','Checkout Clean'
        SPECIAL       = 'SPECIAL',       'Special Request'

    class TaskStatus(models.TextChoices):
        PENDING     = 'PENDING',     'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED   = 'COMPLETED',   'Completed'
        SKIPPED     = 'SKIPPED',     'Skipped'

    room        = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='hk_tasks')
    task_type   = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.DAILY_CLEAN)
    status      = models.CharField(max_length=15, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hk_tasks'
    )
    notes       = models.TextField(blank=True)
    scheduled_date = models.DateField()
    started_at   = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_task_type_display()} — Room {self.room.number} ({self.scheduled_date})"

    class Meta:
        ordering = ['scheduled_date', 'room__number']
