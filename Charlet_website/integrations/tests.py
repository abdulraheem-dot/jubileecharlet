"""
Tests for the integration API on the inner (management) system.

These exercise the JSON endpoints directly with Django's test client, so no
running server is needed.  They verify that bookings arrive from the website,
create/update guests and reservations idempotently, sync cancellations, and
report room availability.
"""

import json
from decimal import Decimal

from django.conf import settings
from django.test import TestCase, Client

from rooms.models import RoomType, Room
from guests.models import Guest
from .models import Reservation, SyncLog


class IntegrationAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room_type = RoomType.objects.create(
            name='Deluxe Room', price_per_night=Decimal('45000.00'), max_occupancy=2
        )
        Room.objects.create(number='101', floor=1, room_type=cls.room_type)

    def setUp(self):
        self.client = Client()
        self.api_key = settings.INTEGRATION_API_KEY
        self.payload = {
            'external_reference': 'JC-TEST1234',
            'guest': {
                'first_name': 'Ada', 'last_name': 'Lovelace',
                'email': 'ada@example.com', 'phone_number': '08012345678',
            },
            'check_in_date': '2026-11-10',
            'check_out_date': '2026-11-12',
            'num_adults': 2,
            'num_children': 0,
            'total_amount': '90000.00',
            'special_requests': 'Late check-in',
            'rooms': [{'name': 'Deluxe Room', 'price_per_night': '45000.00'}],
            'status': 'CONFIRMED',
        }

    def _post(self, url, payload):
        return self.client.post(
            url, data=json.dumps(payload),
            content_type='application/json', HTTP_X_API_KEY=self.api_key,
        )

    # --- auth ---------------------------------------------------------------
    def test_missing_api_key_rejected(self):
        resp = self.client.post(
            '/integrations/api/sync-booking/',
            data=json.dumps({}), content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_wrong_api_key_rejected(self):
        resp = self.client.post(
            '/integrations/api/sync-booking/',
            data=json.dumps({}), content_type='application/json',
            HTTP_X_API_KEY='wrong-key',
        )
        self.assertEqual(resp.status_code, 401)

    # --- sync ---------------------------------------------------------------
    def test_sync_booking_creates_reservation_and_guest(self):
        resp = self._post('/integrations/api/sync-booking/', self.payload)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()['created'])

        res = Reservation.objects.get(external_reference='JC-TEST1234')
        self.assertEqual(res.status, Reservation.Status.CONFIRMED)
        self.assertEqual(res.room_type, self.room_type)
        self.assertEqual(res.guest.email, 'ada@example.com')
        self.assertEqual(res.total_amount, Decimal('90000.00'))
        self.assertEqual(res.num_nights, 2)
        self.assertEqual(SyncLog.objects.filter(result='SUCCESS').count(), 1)

    def test_sync_booking_is_idempotent(self):
        self._post('/integrations/api/sync-booking/', self.payload)
        resp = self._post('/integrations/api/sync-booking/', self.payload)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['created'])
        self.assertEqual(Reservation.objects.filter(external_reference='JC-TEST1234').count(), 1)

    def test_sync_updates_returning_guest(self):
        self._post('/integrations/api/sync-booking/', self.payload)
        # Same email, different phone — should reuse the guest, not create a new one.
        # We intentionally do NOT overwrite existing contact details (staff may have
        # edited them), so the original phone is preserved.
        self.payload['external_reference'] = 'JC-TEST9999'
        self.payload['guest']['phone_number'] = '08099999999'
        self._post('/integrations/api/sync-booking/', self.payload)
        self.assertEqual(Guest.objects.filter(email='ada@example.com').count(), 1)
        self.assertEqual(Guest.objects.get(email='ada@example.com').phone_number, '08012345678')

    def test_sync_does_not_clobber_checked_in_status(self):
        self._post('/integrations/api/sync-booking/', self.payload)
        res = Reservation.objects.get(external_reference='JC-TEST1234')
        res.status = Reservation.Status.CHECKED_IN
        res.save()
        # Re-sync with CONFIRMED — staff already checked the guest in
        self._post('/integrations/api/sync-booking/', self.payload)
        res.refresh_from_db()
        self.assertEqual(res.status, Reservation.Status.CHECKED_IN)

    def test_sync_rejects_missing_dates(self):
        self.payload['check_in_date'] = ''
        resp = self._post('/integrations/api/sync-booking/', self.payload)
        self.assertEqual(resp.status_code, 400)

    # --- cancel -------------------------------------------------------------
    def test_cancel_booking(self):
        self._post('/integrations/api/sync-booking/', self.payload)
        resp = self._post('/integrations/api/cancel-booking/',
                          {'external_reference': 'JC-TEST1234'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Reservation.objects.get(external_reference='JC-TEST1234').status,
                         Reservation.Status.CANCELLED)

    def test_cancel_unknown_reference_is_idempotent(self):
        resp = self._post('/integrations/api/cancel-booking/',
                          {'external_reference': 'JC-NOPE'})
        self.assertEqual(resp.status_code, 200)

    def test_cancel_checked_in_booking_rejected(self):
        self._post('/integrations/api/sync-booking/', self.payload)
        res = Reservation.objects.get(external_reference='JC-TEST1234')
        res.status = Reservation.Status.CHECKED_IN
        res.save()
        resp = self._post('/integrations/api/cancel-booking/',
                          {'external_reference': 'JC-TEST1234'})
        self.assertEqual(resp.status_code, 409)

    # --- availability -------------------------------------------------------
    def test_room_availability_reports_bookable_type(self):
        resp = self.client.get(
            '/integrations/api/room-availability/?check_in=2026-11-10&check_out=2026-11-12',
            HTTP_X_API_KEY=self.api_key,
        )
        self.assertEqual(resp.status_code, 200)
        rt = resp.json()['room_types']['deluxe-room']
        self.assertEqual(rt['name'], 'Deluxe Room')
        self.assertTrue(rt['bookable'])
        self.assertEqual(rt['available'], 1)

    def test_room_availability_blocks_when_reserved_out(self):
        # Reserve the only room of the type for those dates
        self._post('/integrations/api/sync-booking/', self.payload)
        resp = self.client.get(
            '/integrations/api/room-availability/?check_in=2026-11-10&check_out=2026-11-12',
            HTTP_X_API_KEY=self.api_key,
        )
        rt = resp.json()['room_types']['deluxe-room']
        self.assertFalse(rt['bookable'])
        self.assertEqual(rt['available'], 0)

    def test_check_in_converts_reservation_to_stay(self):
        self._post('/integrations/api/sync-booking/', self.payload)
        res = Reservation.objects.get(external_reference='JC-TEST1234')
        room = Room.objects.get(number='101')
        stay = res.check_in(room)
        self.assertTrue(stay.is_active)
        res.refresh_from_db()
        self.assertEqual(res.status, Reservation.Status.CHECKED_IN)
        self.assertEqual(res.assigned_room, room)
