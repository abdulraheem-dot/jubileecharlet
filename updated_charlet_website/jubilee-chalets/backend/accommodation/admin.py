from django.contrib import admin
from .models import Room, RoomCategory, Amenity, RoomImage


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'display_order']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_night', 'max_occupancy', 'is_available', 'is_active']
    list_filter = ['category', 'is_available', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['amenities']
    inlines = [RoomImageInline]
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'category', 'description', 'short_description')}),
        ('Configuration', {'fields': ('max_adults', 'max_children', 'max_occupancy', 'bed_configuration', 'size_sqm', 'floor')}),
        ('Pricing', {'fields': ('price_per_night',)}),
        ('Amenities', {'fields': ('amenities',)}),
        ('Status', {'fields': ('is_available', 'is_active')}),
    )


@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']
