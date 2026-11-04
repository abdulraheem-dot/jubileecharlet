from django.contrib import admin
from .models import FoodCategory, MenuItem, FoodOrder, FoodOrderItem


class FoodOrderItemInline(admin.TabularInline):
    model = FoodOrderItem
    extra = 0


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'price', 'is_available', 'is_vegetarian']
    list_filter   = ['category', 'is_available']
    list_editable = ['is_available', 'price']

@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'room', 'guest', 'status', 'created_at']
    list_filter  = ['status']
    inlines      = [FoodOrderItemInline]
