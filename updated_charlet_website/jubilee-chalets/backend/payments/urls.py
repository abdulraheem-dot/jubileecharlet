from django.urls import path
from . import views

urlpatterns = [
    path('initialize/', views.initialize_payment, name='payment-initialize'),
    path('verify/<str:reference>/', views.verify_payment, name='payment-verify'),
    path('webhook/', views.paystack_webhook, name='payment-webhook'),
]
