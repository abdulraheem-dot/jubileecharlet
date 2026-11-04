from django.contrib import admin
from .models import Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_free', 'price', 'is_active', 'display_order']
    list_filter = ['category', 'is_free', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['display_order', 'is_active']
