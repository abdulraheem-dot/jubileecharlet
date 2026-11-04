from django.contrib import admin
from .models import EventVenue, EventEnquiry


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'is_active']


@admin.register(EventEnquiry)
class EventEnquiryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'event_type', 'event_date', 'expected_attendees', 'status', 'created_at']
    list_filter = ['status', 'catering_required']
    search_fields = ['full_name', 'email', 'event_type']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
