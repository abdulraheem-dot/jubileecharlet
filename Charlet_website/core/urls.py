"""
core/urls.py

Core app URL patterns.
The core app handles:
- The home/landing page
- The smart dashboard router (redirects user to correct dashboard based on role)
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',           views.home,      name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
