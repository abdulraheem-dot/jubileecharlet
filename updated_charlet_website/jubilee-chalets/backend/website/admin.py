from django.contrib import admin
from .models import WebsiteSettings


@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Info', {'fields': ('site_name', 'tagline')}),
        ('Contact', {'fields': ('phone_primary', 'phone_secondary', 'email_primary', 'email_bookings', 'address', 'city', 'state', 'country', 'whatsapp_number')}),
        ('Social Media', {'fields': ('facebook_url', 'instagram_url', 'twitter_url')}),
        ('Operations', {'fields': ('check_in_time', 'check_out_time', 'google_maps_embed_url')}),
        ('Policies', {'fields': ('cancellation_policy', 'privacy_policy', 'terms_conditions')}),
    )

    def has_add_permission(self, request):
        return not WebsiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
