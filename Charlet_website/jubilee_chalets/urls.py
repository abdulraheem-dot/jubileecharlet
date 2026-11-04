"""
Main URL Configuration for Jubilee Chalets Hotel Management System.

Django uses URL patterns to decide which view handles each web request.
Each app has its own urls.py file and we include them all here.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel — only for super admins
    path('admin/', admin.site.urls),

    # Core app — home page, dashboard router
    path('', include('core.urls')),

    # Accounts — login, logout, staff profile, role management
    path('accounts/', include('accounts.urls')),

    # Rooms — room list, room detail, QR code views
    path('rooms/', include('rooms.urls')),

    # Guests — guest portal, guest profile, check-in/check-out
    path('guests/', include('guests.urls')),

    # Service Requests — the heart of the system
    # Guests submit requests; staff manage them
    path('requests/', include('requests_app.urls')),

    # Notifications — in-app alerts for staff and guests
    path('notifications/', include('notifications.urls')),

    # Restaurant — menu, food orders, order tracking
    path('restaurant/', include('restaurant.urls')),

    # Housekeeping — room cleaning tasks and status
    path('housekeeping/', include('housekeeping.urls')),

    # Maintenance — maintenance records and assignments
    path('maintenance/', include('maintenance.urls')),

    # Inventory — stock levels, low-stock alerts
    path('inventory/', include('inventory.urls')),

    # Feedback — guest ratings and complaints
    path('feedback/', include('feedback.urls')),

    # Reports — analytics, charts, management reports
    path('reports/', include('reports.urls')),

    # Integrations — API for the public booking website
    # (receives confirmed bookings; exposes room availability)
    path('integrations/api/', include('integrations.urls')),
]

# Serve media files (uploaded images, QR codes) during development
# In production, a web server like Nginx handles this instead.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
