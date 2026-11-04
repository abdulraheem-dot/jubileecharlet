from rest_framework import serializers
from .models import EventVenue, EventEnquiry


class EventVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVenue
        fields = ['id', 'name', 'description', 'capacity', 'amenities', 'images', 'is_active']


class EventEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventEnquiry
        fields = ['id', 'full_name', 'email', 'phone_number', 'event_type', 'event_date',
                  'expected_attendees', 'venue', 'message', 'catering_required', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_event_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError('Event date cannot be in the past.')
        return value
