"""
accounts/urls.py

URL patterns for the accounts app.

Each path() call maps a URL to a view function.
The 'name' parameter lets us reference URLs in templates using {% url 'accounts:login' %}
instead of hardcoding '/accounts/login/' — this means if we ever change the URL,
we only update it in one place.

The app_name creates a namespace: all names are prefixed with 'accounts:'
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Current user's own profile
    path('profile/',        views.my_profile,    name='my_profile'),
    path('profile/duty/',   views.toggle_duty,   name='toggle_duty'),

    # Staff management (manager/admin only)
    path('staff/',                  views.staff_list,       name='staff_list'),
    path('staff/new/',              views.staff_create,     name='staff_create'),
    path('staff/<int:pk>/',         views.staff_detail,     name='staff_detail'),
    path('staff/<int:pk>/edit/',    views.staff_edit,       name='staff_edit'),
    path('staff/<int:pk>/deactivate/', views.staff_deactivate, name='staff_deactivate'),

    # Remove any user (deactivates + logs them out)
    path('users/<int:pk>/remove/', views.remove_user, name='remove_user'),
]
