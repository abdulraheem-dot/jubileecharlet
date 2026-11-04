from django.contrib import admin
from .models import MaintenanceRecord

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display  = ['room', 'category', 'title', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter   = ['status', 'priority', 'category']
    search_fields = ['title', 'room__number']
    list_editable = ['status', 'assigned_to']
