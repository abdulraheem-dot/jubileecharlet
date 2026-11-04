from django.contrib import admin
from .models import Guest, GuestStay


class GuestStayInline(admin.TabularInline):
    model = GuestStay
    extra = 0
    readonly_fields = ['checked_in_by', 'checked_out_by', 'check_in_date', 'actual_checkout']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display  = ['get_full_name', 'email', 'phone_number', 'is_vip', 'created_at']
    list_filter   = ['is_vip', 'nationality']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    inlines       = [GuestStayInline]

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(GuestStay)
class GuestStayAdmin(admin.ModelAdmin):
    list_display  = ['guest', 'room', 'check_in_date', 'expected_checkout', 'is_active']
    list_filter   = ['is_active', 'room__floor']
    search_fields = ['guest__first_name', 'guest__last_name', 'room__number']
    readonly_fields = ['checked_in_by', 'checked_out_by']
