"""
integrations/client.py

Thin HTTP client that talks to the inner hotel management system ("PMS").

The PMS exposes a small JSON API protected by a shared API key.  This client
wraps ``requests`` so the rest of the codebase doesn't deal with URLs, headers
or timeouts directly.

Configuration (settings.py / .env):
    PMS_BASE_URL  — e.g. http://localhost:8001  (the management system's URL)
    PMS_API_KEY   — must match the PMS's INTEGRATION_API_KEY
    PMS_TIMEOUT   — per-request timeout in seconds (default 10)

If the PMS is not configured (no base URL / key) every method is a safe no-op,
so the booking site keeps working standalone.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger('jubilee')


class PMSNotConfigured(Exception):
    """Raised internally when the PMS connection details are missing."""


class PMSClient:
    def __init__(self):
        self.base_url = (getattr(settings, 'PMS_BASE_URL', '') or '').strip().rstrip('/')
        self.api_key = (getattr(settings, 'PMS_API_KEY', '') or '').strip()
        self.timeout = getattr(settings, 'PMS_TIMEOUT', 10)

    @property
    def configured(self):
        """True only when we have both a URL and a non-placeholder key."""
        return bool(self.base_url and self.api_key
                    and not self.api_key.startswith('changeme'))

    def _url(self, path):
        return f'{self.base_url}/integrations/api/{path}'

    def _headers(self):
        return {'X-API-Key': self.api_key, 'Content-Type': 'application/json'}

    def sync_booking(self, payload):
        if not self.configured:
            raise PMSNotConfigured
        resp = requests.post(
            self._url('sync-booking/'),
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def cancel_booking(self, external_reference):
        if not self.configured:
            raise PMSNotConfigured
        resp = requests.post(
            self._url('cancel-booking/'),
            json={'external_reference': external_reference},
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def get_room_availability(self, check_in, check_out):
        if not self.configured:
            raise PMSNotConfigured
        resp = requests.get(
            self._url('room-availability/'),
            params={'check_in': check_in, 'check_out': check_out},
            headers={'X-API-Key': self.api_key},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
