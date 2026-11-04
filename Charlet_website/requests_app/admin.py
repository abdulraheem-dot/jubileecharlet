from django.contrib import admin
from .models import ServiceRequest, AuditLog, Message


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    readonly_fields = ['user', 'action', 'notes', 'created_at']
    can_delete = False


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender_staff', 'is_from_guest', 'content', 'created_at']
    can_delete = False


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display  = ['request_number', 'title', 'room', 'status', 'priority', 'department', 'assigned_to', 'created_at']
    list_filter   = ['status', 'priority', 'department', 'category']
    search_fields = ['request_number', 'title', 'room__number']
    readonly_fields = ['request_number', 'created_at', 'updated_at', 'completed_at']
    inlines = [AuditLogInline, MessageInline]
    date_hierarchy = 'created_at'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ['created_at', 'user', 'action', 'request']
    list_filter   = ['action']
    readonly_fields = ['user', 'request', 'action', 'notes', 'created_at']
