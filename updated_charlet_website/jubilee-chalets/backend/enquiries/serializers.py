from rest_framework import serializers
from .models import ContactEnquiry, Testimonial, FAQ, NewsletterSubscription


class ContactEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEnquiry
        fields = ['id', 'full_name', 'email', 'phone_number', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'guest_name', 'review_text', 'rating', 'visit_date', 'is_approved']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'display_order']


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'consent']

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError('You must consent to subscribe.')
        return value

    def create(self, validated_data):
        obj, created = NewsletterSubscription.objects.update_or_create(
            email=validated_data['email'],
            defaults={'consent': validated_data['consent'], 'is_active': True},
        )
        return obj
