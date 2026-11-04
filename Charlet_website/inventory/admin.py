from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display  = ['name', 'department', 'quantity', 'unit', 'minimum_level', 'is_low_stock']
    list_filter   = ['department']
    search_fields = ['name']
    list_editable = ['quantity']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock?'
