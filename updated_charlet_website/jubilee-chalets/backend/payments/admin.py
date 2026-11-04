from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'booking', 'amount', 'status', 'channel', 'paid_at', 'created_at']
    list_filter = ['status', 'channel']
    search_fields = ['reference', 'booking__booking_reference']
    readonly_fields = ['reference', 'amount', 'paystack_id', 'webhook_events_processed', 'created_at', 'updated_at']
