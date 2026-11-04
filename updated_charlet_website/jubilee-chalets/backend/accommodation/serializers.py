from rest_framework import serializers
from .models import Room, RoomCategory, Amenity, RoomImage


class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = ['id', 'name', 'slug', 'description']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class RoomListSerializer(serializers.ModelSerializer):
    category = RoomCategorySerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'category', 'short_description',
            'max_adults', 'max_children', 'max_occupancy', 'bed_configuration',
            'size_sqm', 'price_per_night', 'is_available', 'amenities',
            'images', 'primary_image',
        ]

    def get_primary_image(self, obj):
        request = self.context.get('request')
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not img:
            return None
        if request:
            return request.build_absolute_uri(img.image.url)
        return img.image.url


class RoomDetailSerializer(RoomListSerializer):
    class Meta(RoomListSerializer.Meta):
        fields = RoomListSerializer.Meta.fields + ['description', 'floor']
