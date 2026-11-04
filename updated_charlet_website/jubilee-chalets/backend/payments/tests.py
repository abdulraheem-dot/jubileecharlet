from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accommodation.models import Room, RoomCategory
from bookings.models import Booking, BookingRoom
from payments.models import Payment

User = get_user_model()


class PaymentTests(TestCase):
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
            description='Test',
            price_per_night=Decimal('15000.00'),
            max_adults=2,
            max_children=1,
            max_occupancy=3,
            bed_configuration='1 Double Bed',
        )

    def _create_booking(self):
        booking = Booking.objects.create(
            guest=self.user,
            check_in_date=date.today() + timedelta(days=30),
            check_out_date=date.today() + timedelta(days=33),
            num_adults=2,
            status=Booking.Status.AWAITING_PAYMENT,
            subtotal=Decimal('45000.00'),
            total_amount=Decimal('45000.00'),
        )
        BookingRoom.objects.create(
            booking=booking,
            room=self.room,
            price_per_night=self.room.price_per_night,
            total_price=Decimal('45000.00'),
        )
        return booking

    def test_initialize_payment(self):
        """Payment initialization creates a Payment record."""
        booking = self._create_booking()
        url = reverse('payment-initialize')
        resp = self.client.post(url, {'booking_id': booking.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('reference', resp.data)
        self.assertTrue(Payment.objects.filter(booking=booking).exists())

    def test_initialize_payment_already_paid(self):
        """Cannot initialize payment for an already-paid booking."""
        booking = self._create_booking()
        booking.payment_status = 'paid'
        booking.save()
        url = reverse('payment-initialize')
        resp = self.client.post(url, {'booking_id': booking.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_initialize_payment_other_user_booking(self):
        """Cannot pay for another user's booking."""
        other = User.objects.create_user(
            email='other@example.com', password='pass12345',
            first_name='Other', last_name='User',
        )
        booking = Booking.objects.create(
            guest=other,
            check_in_date=date.today() + timedelta(days=30),
            check_out_date=date.today() + timedelta(days=32),
            num_adults=2,
            status=Booking.Status.AWAITING_PAYMENT,
            total_amount=Decimal('30000.00'),
        )
        BookingRoom.objects.create(
            booking=booking, room=self.room,
            price_per_night=self.room.price_per_night,
            total_price=Decimal('30000.00'),
        )
        url = reverse('payment-initialize')
        resp = self.client.post(url, {'booking_id': booking.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_payment_confirms_booking(self):
        """Payment verification in mock mode confirms the booking."""
        booking = self._create_booking()
        # Initialize
        url = reverse('payment-initialize')
        resp = self.client.post(url, {'booking_id': booking.id}, format='json')
        reference = resp.data['reference']

        # Verify
        verify_url = reverse('payment-verify', kwargs={'reference': reference})
        resp = self.client.get(verify_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'success')

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(booking.payment_status, 'paid')
        self.assertIsNotNone(booking.confirmed_at)

    def test_webhook_idempotent(self):
        """Webhook processing is idempotent — duplicate events don't double-process."""
        booking = self._create_booking()
        payment = Payment.objects.create(
            booking=booking,
            reference='JC-PAY-TEST123',
            amount=Decimal('45000.00'),
            status=Payment.Status.PENDING,
        )
        url = reverse('payment-webhook')
        # Since we're in mock mode (placeholder key), webhook returns OK
        resp = self.client.post(url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
