from django.contrib import admin
from .models import Booking, BookingRoom, CancellationRequest


class BookingRoomInline(admin.TabularInline):
    model = BookingRoom
    extra = 0
    readonly_fields = ['price_per_night', 'total_price']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'guest', 'check_in_date', 'check_out_date', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'check_in_date']
    search_fields = ['booking_reference', 'guest__email', 'guest__first_name', 'guest__last_name']
    readonly_fields = ['booking_reference', 'subtotal', 'taxes_fees', 'total_amount', 'created_at', 'updated_at']
    inlines = [BookingRoomInline]
    fieldsets = (
        ('Booking Info', {'fields': ('booking_reference', 'guest', 'status', 'payment_status')}),
        ('Dates & Guests', {'fields': ('check_in_date', 'check_out_date', 'num_adults', 'num_children', 'special_requests')}),
        ('Financials', {'fields': ('subtotal', 'taxes_fees', 'total_amount')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'confirmed_at', 'checked_in_at', 'checked_out_at')}),
    )
    date_hierarchy = 'check_in_date'


@admin.register(CancellationRequest)
class CancellationRequestAdmin(admin.ModelAdmin):
    list_display = ['booking', 'requested_at', 'is_approved', 'reviewed_by']
    list_filter = ['is_approved']
    readonly_fields = ['requested_at']
