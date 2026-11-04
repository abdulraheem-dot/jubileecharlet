from django.contrib import admin
from .models import Feedback, Complaint

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['request', 'guest', 'rating', 'created_at']
    list_filter  = ['rating']

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'room', 'guest', 'category', 'priority', 'status', 'created_at']
    list_filter   = ['status', 'category', 'priority']
    list_editable = ['status', 'assigned_to'] if False else ['status']
