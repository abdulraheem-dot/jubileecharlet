from rest_framework import serializers
from .models import MenuCategory, MenuItem


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description', 'display_order']


class MenuItemSerializer(serializers.ModelSerializer):
    category = MenuCategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'category', 'name', 'description', 'price', 'image',
                  'is_available', 'is_vegetarian', 'is_vegan', 'is_gluten_free',
                  'allergens', 'display_order']
