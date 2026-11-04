"""
Tests for the outer (booking) side of the PMS integration.

The PMS itself is mocked, so these run without the inner system online.
They verify that:
 - booking syncs build the correct payload and push to the PMS
 - cancellations are pushed
 - the PMS availability filter blocks unbookable rooms
 - everything degrades gracefully when the PMS isn't configured / is down
"""

from decimal import Decimal
from datetime import date
from unittest.mock import patch

from django.test import TestCase, override_settings

from accounts.models import User
from accommodation.models import RoomCategory, Room
from bookings.models import Booking, BookingRoom
from integrations import services


class PMSIntegrationDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='guest@example.com', password='demo12345',
            first_name='Ada', last_name='Lovelace', phone_number='08012345678',
        )
        cls.category = RoomCategory.objects.create(name='Standard')
        cls.room = Room.objects.create(
            name='Deluxe Room', category=cls.category,
            price_per_night=Decimal('45000.00'), max_adults=2,
        )
        cls.booking = Booking.objects.create(
            guest=cls.user,
            check_in_date=date(2026, 11, 10), check_out_date=date(2026, 11, 12),
            num_adults=2, num_children=0, status=Booking.Status.AWAITING_PAYMENT,
        )
        BookingRoom.objects.create(
            booking=cls.booking, room=cls.room, price_per_night=cls.room.price_per_night,
        )


class SyncNotConfiguredTests(TestCase):
    def test_sync_returns_none_when_not_configured(self):
        booking = Booking(guest=None)  # not saved; not used
        self.assertIsNone(services.sync_booking_to_pms(booking))

    def test_unavailable_rooms_empty_when_not_configured(self):
        self.assertEqual(
            services.get_pms_unavailable_rooms([], '2026-11-10', '2026-11-12'),
            [],
        )


@patch('integrations.services.PMSClient')
class SyncConfiguredTests(PMSIntegrationDataMixin, TestCase):
    def test_sync_builds_payload_and_pushes(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.sync_booking.return_value = {'status': 'ok', 'created': True}

        result = services.sync_booking_to_pms(self.booking)

        client.sync_booking.assert_called_once()
        payload = client.sync_booking.call_args.args[0]
        self.assertEqual(payload['external_reference'], self.booking.booking_reference)
        self.assertEqual(payload['guest']['email'], 'guest@example.com')
        self.assertEqual(payload['guest']['phone_number'], '08012345678')
        self.assertEqual(payload['check_in_date'], '2026-11-10')
        self.assertEqual(payload['check_out_date'], '2026-11-12')
        self.assertEqual(len(payload['rooms']), 1)
        self.assertEqual(payload['rooms'][0]['name'], 'Deluxe Room')
        self.assertEqual(payload['status'], 'CONFIRMED')
        self.assertEqual(result, {'status': 'ok', 'created': True})

    def test_sync_swallows_pms_failure(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.sync_booking.side_effect = Exception('PMS down')
        self.assertIsNone(services.sync_booking_to_pms(self.booking))


@patch('integrations.services.PMSClient')
class CancelConfiguredTests(PMSIntegrationDataMixin, TestCase):
    def test_cancel_pushes_reference(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.cancel_booking.return_value = {'status': 'ok'}
        services.cancel_booking_in_pms(self.booking)
        client.cancel_booking.assert_called_once()
        self.assertEqual(client.cancel_booking.call_args.args[0],
                         self.booking.booking_reference)


@patch('integrations.services.PMSClient')
class RoomTypeMappingTests(PMSIntegrationDataMixin, TestCase):
    """PMS_ROOM_TYPE_MAP lets the two systems use different room names."""

    def test_explicit_mapping_used_in_booking_payload(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.sync_booking.return_value = {'status': 'ok'}

        with override_settings(PMS_ROOM_TYPE_MAP={'deluxe-room': 'Deluxe Suite'}):
            services.sync_booking_to_pms(self.booking)

        payload = client.sync_booking.call_args.args[0]
        # The website room is "Deluxe Room" but maps to the PMS "Deluxe Suite"
        self.assertEqual(payload['rooms'][0]['name'], 'Deluxe Suite')

    def test_mapping_drives_availability_lookup(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.return_value = {
            'room_types': {'deluxe-suite': {'name': 'Deluxe Suite', 'bookable': False, 'available': 0}}
        }

        with override_settings(PMS_ROOM_TYPE_MAP={'deluxe-room': 'Deluxe Suite'}):
            unavail = services.get_pms_unavailable_rooms(
                [self.room], date(2026, 11, 10), date(2026, 11, 12)
            )
        # The room is reported by its own name, but matched via the mapping
        self.assertEqual(unavail, ['Deluxe Room'])


@patch('integrations.services.PMSClient')
class AvailabilityMergeTests(PMSIntegrationDataMixin, TestCase):
    def test_blocks_unbookable_rooms(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.return_value = {
            'room_types': {'deluxe-room': {'name': 'Deluxe Room', 'bookable': False, 'available': 0}}
        }
        unavail = services.get_pms_unavailable_rooms([self.room], '2026-11-10', '2026-11-12')
        self.assertEqual(unavail, ['Deluxe Room'])

    def test_allows_bookable_rooms(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.return_value = {
            'room_types': {'deluxe-room': {'name': 'Deluxe Room', 'bookable': True, 'available': 1}}
        }
        self.assertEqual(
            services.get_pms_unavailable_rooms([self.room], '2026-11-10', '2026-11-12'),
            [],
        )

    def test_falls_back_on_pms_error(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.side_effect = Exception('timeout')
        self.assertEqual(
            services.get_pms_unavailable_rooms([self.room], '2026-11-10', '2026-11-12'),
            [],
        )


@patch('integrations.services.PMSClient')
class SignalTests(PMSIntegrationDataMixin, TestCase):
    """Verify that real booking status transitions trigger PMS sync/cancel."""

    def test_confirm_triggers_pms_sync(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.sync_booking.return_value = {'status': 'ok', 'created': True}

        with self.captureOnCommitCallbacks(execute=True):
            self.booking.status = Booking.Status.CONFIRMED
            self.booking.save()

        client.sync_booking.assert_called_once()

    def test_cancel_triggers_pms_cancel(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.cancel_booking.return_value = {'status': 'ok'}

        with self.captureOnCommitCallbacks(execute=True):
            self.booking.status = Booking.Status.CANCELLED
            self.booking.save()

        client.cancel_booking.assert_called_once()
