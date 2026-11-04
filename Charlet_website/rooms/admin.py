from django.contrib import admin
from django.utils.html import format_html
from .models import Room, RoomType, RoomStatus


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'price_per_night', 'max_occupancy', 'bed_type', 'has_ac', 'has_wifi']
    list_filter   = ['has_ac', 'has_tv', 'has_wifi', 'has_minibar']
    search_fields = ['name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ['number', 'floor', 'room_type', 'status_badge', 'housekeeping_status', 'qr_preview']
    list_filter   = ['status', 'housekeeping_status', 'floor', 'room_type']
    search_fields = ['number']
    readonly_fields = ['access_token', 'qr_code', 'qr_preview_large']
    list_editable = ['housekeeping_status']

    actions = ['mark_available', 'mark_cleaning', 'regenerate_qr_codes']

    def status_badge(self, obj):
        colours = {
            'AVAILABLE': '#10b981', 'OCCUPIED': '#3b82f6',
            'RESERVED': '#0ea5e9', 'CLEANING': '#f59e0b',
            'MAINTENANCE': '#ef4444', 'OUT_OF_SERVICE': '#6b7280'
        }
        colour = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;border-radius:12px;font-size:0.75rem;">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="40" height="40" />', obj.qr_code.url)
        return '—'
    qr_preview.short_description = 'QR'

    def qr_preview_large(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="200" height="200" />', obj.qr_code.url)
        return 'Not generated yet'
    qr_preview_large.short_description = 'QR Code Preview'

    @admin.action(description='Mark selected rooms as Available')
    def mark_available(self, request, queryset):
        queryset.update(status=RoomStatus.AVAILABLE)

    @admin.action(description='Mark selected rooms as Cleaning')
    def mark_cleaning(self, request, queryset):
        queryset.update(status=RoomStatus.CLEANING)

    @admin.action(description='Re-generate QR codes')
    def regenerate_qr_codes(self, request, queryset):
        for room in queryset:
            room.qr_code = None
            room.generate_qr_code()
            Room.objects.filter(pk=room.pk).update(qr_code=room.qr_code)
        self.message_user(request, f"QR codes regenerated for {queryset.count()} rooms.")
