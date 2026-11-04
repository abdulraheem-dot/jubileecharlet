from rest_framework import serializers
from .models import Experience


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'title', 'slug', 'description', 'short_description', 'image', 'category', 'price', 'is_free', 'is_active', 'display_order']
