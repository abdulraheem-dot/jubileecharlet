from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_view, name='auth-register'),
    path('login/', views.login_view, name='auth-login'),
    path('logout/', views.logout_view, name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', views.profile_view, name='auth-profile'),
    path('password-change/', views.change_password_view, name='auth-change-password'),
    path('password-reset/', views.password_reset_request_view, name='auth-password-reset'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='auth-password-reset-confirm'),
]
