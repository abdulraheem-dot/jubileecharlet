from django.contrib import admin
from .models import HousekeepingTask

@admin.register(HousekeepingTask)
class HousekeepingTaskAdmin(admin.ModelAdmin):
    list_display  = ['room', 'task_type', 'status', 'assigned_to', 'scheduled_date']
    list_filter   = ['status', 'task_type', 'scheduled_date']
    list_editable = ['status', 'assigned_to']
