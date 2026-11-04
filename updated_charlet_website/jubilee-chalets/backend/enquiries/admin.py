from django.contrib import admin
from .models import ContactEnquiry, Testimonial, FAQ, NewsletterSubscription


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['full_name', 'email', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'rating', 'visit_date', 'is_approved']
    list_filter = ['is_approved', 'rating']
    list_editable = ['is_approved']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'display_order', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['display_order', 'is_active']


@admin.register(NewsletterSubscription)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active']
    search_fields = ['email']
