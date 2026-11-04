"""
integrations/admin.py

Makes website reservations and sync logs visible in the staff admin so
reception/management can see online bookings arriving in real time.
"""

from django.contrib import admin
from .models import Reservation, SyncLog


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'external_reference', 'guest', 'room_type',
        'check_in_date', 'check_out_date',
        'num_adults', 'total_amount', 'status', 'synced_at',
    )
    list_filter = ('status', 'source', 'room_type')
    search_fields = ('external_reference', 'guest__first_name', 'guest__last_name', 'guest__email')
    readonly_fields = ('synced_at', 'created_at', 'updated_at')
    date_hierarchy = 'check_in_date'
    ordering = ('-created_at',)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'external_reference', 'result', 'created_at')
    list_filter = ('endpoint', 'result')
    search_fields = ('external_reference', 'message')
    readonly_fields = ('endpoint', 'external_reference', 'result', 'message', 'payload', 'created_at')
