"""
integrations/urls.py

URL routes for the website → PMS integration API.

All endpoints live under /integrations/api/ and require an X-API-Key header.
"""

from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # Receive a confirmed (or updated) booking from the website
    path('sync-booking/', views.sync_booking, name='sync-booking'),
    # Mark a website booking as cancelled
    path('cancel-booking/', views.cancel_booking, name='cancel-booking'),
    # Report room-type availability back to the website (source of truth for
    # physical room status: maintenance, out-of-service, occupied, etc.)
    path('room-availability/', views.room_availability, name='room-availability'),
]
