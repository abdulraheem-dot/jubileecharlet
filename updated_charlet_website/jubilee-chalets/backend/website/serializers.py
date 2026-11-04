from rest_framework import serializers
from .models import WebsiteSettings


class WebsiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteSettings
        exclude = ['id', 'cancellation_policy', 'privacy_policy', 'terms_conditions']
