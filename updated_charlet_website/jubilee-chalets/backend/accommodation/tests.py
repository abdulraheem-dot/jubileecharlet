from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from accommodation.models import RoomCategory, Room


class CheckAvailabilityPMSTests(TestCase):
    """The date-aware availability search merges in the PMS's physical status."""

    @classmethod
    def setUpTestData(cls):
        cls.category = RoomCategory.objects.create(name='Standard')
        cls.room = Room.objects.create(
            name='Deluxe Room', category=cls.category,
            price_per_night=Decimal('45000.00'), max_adults=2,
        )

    def setUp(self):
        self.client = APIClient()
        self.url = ('/api/rooms/availability/'
                    '?check_in=2026-11-10&check_out=2026-11-12&num_adults=1')

    def test_returns_room_when_pms_not_configured(self):
        # PMS not configured → graceful fallback; room still shows as available
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        names = [r['name'] for r in resp.json()]
        self.assertIn('Deluxe Room', names)

    @patch('integrations.services.PMSClient')
    def test_excludes_room_pms_says_unbookable(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.return_value = {
            'room_types': {'deluxe-room': {'name': 'Deluxe Room', 'bookable': False, 'available': 0}}
        }
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        names = [r['name'] for r in resp.json()]
        self.assertNotIn('Deluxe Room', names)

    @patch('integrations.services.PMSClient')
    def test_keeps_room_pms_says_bookable(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.return_value = {
            'room_types': {'deluxe-room': {'name': 'Deluxe Room', 'bookable': True, 'available': 1}}
        }
        resp = self.client.get(self.url)
        names = [r['name'] for r in resp.json()]
        self.assertIn('Deluxe Room', names)

    @patch('integrations.services.PMSClient')
    def test_falls_back_when_pms_errors(self, MockClient):
        client = MockClient.return_value
        client.configured = True
        client.get_room_availability.side_effect = Exception('PMS unreachable')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        names = [r['name'] for r in resp.json()]
        self.assertIn('Deluxe Room', names)
