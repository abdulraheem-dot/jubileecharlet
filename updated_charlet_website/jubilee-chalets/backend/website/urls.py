from django.urls import path
from . import views
from bookings.views import dashboard_summary

urlpatterns = [
    path('website/settings/', views.get_settings, name='website-settings'),
    path('dashboard/summary/', dashboard_summary, name='dashboard-summary'),
    path('admin/dashboard/', views.dashboard_summary_admin, name='admin-dashboard-summary'),
]
