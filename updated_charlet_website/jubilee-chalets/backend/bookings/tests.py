from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accommodation.models import Room, RoomCategory
from bookings.models import Booking, BookingRoom

User = get_user_model()


class BookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
        self.client.force_authenticate(user=self.user)

        self.category = RoomCategory.objects.create(name='Standard', slug='standard')
        self.room = Room.objects.create(
            name='Test Room',
            slug='test-room',
            category=self.category,
            description='Test description',
            short_description='Test',
            price_per_night=Decimal('15000.00'),
            max_adults=2,
            max_children=1,
            max_occupancy=3,
            bed_configuration='1 Double Bed',
        )

    def test_create_booking(self):
        """Booking creation with valid data should succeed."""
        url = reverse('booking-list-create')
        data = {
            'room_ids': [self.room.id],
            'check_in_date': (date.today() + timedelta(days=30)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=33)).isoformat(),
            'num_adults': 2,
            'num_children': 0,
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['status'], 'awaiting_payment')
        self.assertEqual(resp.data['num_nights'], 3)
        self.assertEqual(Decimal(resp.data['total_amount']), Decimal('45000.00'))

    def test_prevent_double_booking(self):
        """Booking the same room for overlapping dates should fail with 409."""
        url = reverse('booking-list-create')
        check_in = (date.today() + timedelta(days=30)).isoformat()
        check_out = (date.today() + timedelta(days=33)).isoformat()

        # First booking
        resp1 = self.client.post(url, {
            'room_ids': [self.room.id],
            'check_in_date': check_in,
            'check_out_date': check_out,
            'num_adults': 2,
        }, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Overlapping booking should fail
        resp2 = self.client.post(url, {
            'room_ids': [self.room.id],
            'check_in_date': (date.today() + timedelta(days=31)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=32)).isoformat(),
            'num_adults': 2,
        }, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_409_CONFLICT)

    def test_booking_requires_auth(self):
        """Unauthenticated users cannot create bookings."""
        self.client.force_authenticate(user=None)
        url = reverse('booking-list-create')
        resp = self.client.post(url, {
            'room_ids': [self.room.id],
            'check_in_date': (date.today() + timedelta(days=30)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=32)).isoformat(),
            'num_adults': 2,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_see_own_bookings(self):
        """Users should only see their own bookings."""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User',
        )
        booking = Booking.objects.create(
            guest=other_user,
            check_in_date=date.today() + timedelta(days=30),
            check_out_date=date.today() + timedelta(days=32),
            num_adults=2,
            status=Booking.Status.CONFIRMED,
        )
        BookingRoom.objects.create(
            booking=booking,
            room=self.room,
            price_per_night=self.room.price_per_night,
        )

        url = reverse('booking-list-create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 0)

    def test_invalid_dates(self):
        """Check-out before check-in should fail."""
        url = reverse('booking-list-create')
        resp = self.client.post(url, {
            'room_ids': [self.room.id],
            'check_in_date': (date.today() + timedelta(days=30)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=30)).isoformat(),
            'num_adults': 2,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exceed_occupancy(self):
        """Booking with more adults than room allows should fail."""
        url = reverse('booking-list-create')
        resp = self.client.post(url, {
            'room_ids': [self.room.id],
            'check_in_date': (date.today() + timedelta(days=30)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=32)).isoformat(),
            'num_adults': 5,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class AvailabilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = RoomCategory.objects.create(name='Standard', slug='standard')
        self.room = Room.objects.create(
            name='Test Room',
            slug='test-room',
            category=self.category,
            description='Test',
            price_per_night=Decimal('15000.00'),
            max_adults=2,
            max_children=1,
            max_occupancy=3,
            bed_configuration='1 Double Bed',
        )
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )

    def test_available_room_shown(self):
        """Available rooms should be returned."""
        url = reverse('room-availability')
        resp = self.client.get(url, {
            'check_in': (date.today() + timedelta(days=30)).isoformat(),
            'check_out': (date.today() + timedelta(days=32)).isoformat(),
            'num_adults': 2,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_booked_room_excluded(self):
        """Booked rooms should be excluded from availability."""
        booking = Booking.objects.create(
            guest=self.user,
            check_in_date=date.today() + timedelta(days=30),
            check_out_date=date.today() + timedelta(days=32),
            num_adults=2,
            status=Booking.Status.CONFIRMED,
        )
        BookingRoom.objects.create(
            booking=booking,
            room=self.room,
            price_per_night=self.room.price_per_night,
        )
        url = reverse('room-availability')
        resp = self.client.get(url, {
            'check_in': (date.today() + timedelta(days=30)).isoformat(),
            'check_out': (date.today() + timedelta(days=32)).isoformat(),
            'num_adults': 2,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)
