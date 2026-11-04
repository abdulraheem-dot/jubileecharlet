from django.contrib import admin
from .models import MenuCategory, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ['name', 'price', 'is_available', 'is_vegetarian', 'display_order']


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order']
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_vegetarian', 'is_vegan']
    list_filter = ['category', 'is_available', 'is_vegetarian']
    search_fields = ['name']
    list_editable = ['is_available', 'price']
