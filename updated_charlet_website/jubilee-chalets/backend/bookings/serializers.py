from rest_framework import serializers
from django.utils import timezone
from .models import Booking, BookingRoom, CancellationRequest
from accommodation.serializers import RoomListSerializer


class BookingRoomSerializer(serializers.ModelSerializer):
    room = RoomListSerializer(read_only=True)

    class Meta:
        model = BookingRoom
        fields = ['id', 'room', 'price_per_night', 'total_price']


class BookingSerializer(serializers.ModelSerializer):
    rooms = BookingRoomSerializer(source='booking_rooms', many=True, read_only=True)
    num_nights = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'status', 'payment_status',
            'check_in_date', 'check_out_date', 'num_adults', 'num_children',
            'num_nights', 'rooms', 'subtotal', 'taxes_fees', 'total_amount',
            'special_requests', 'created_at', 'updated_at', 'confirmed_at',
            'checked_in_at', 'checked_out_at',
        ]
        read_only_fields = [
            'id', 'booking_reference', 'status', 'payment_status',
            'subtotal', 'taxes_fees', 'total_amount', 'created_at',
            'updated_at', 'confirmed_at', 'checked_in_at', 'checked_out_at',
        ]


class CreateBookingSerializer(serializers.Serializer):
    room_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1, max_length=10)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    num_adults = serializers.IntegerField(min_value=1, max_value=20)
    num_children = serializers.IntegerField(min_value=0, max_value=20, default=0)
    special_requests = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate_check_in_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('Check-in date cannot be in the past.')
        return value

    def validate(self, attrs):
        if attrs['check_out_date'] <= attrs['check_in_date']:
            raise serializers.ValidationError({'check_out_date': 'Check-out must be after check-in.'})
        return attrs


class CancellationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationRequest
        fields = ['id', 'reason', 'requested_at', 'is_approved']
        read_only_fields = ['id', 'requested_at', 'is_approved']
