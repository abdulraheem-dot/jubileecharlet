from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Staff
    path('',                        views.dashboard,           name='dashboard'),
    path('order/<int:pk>/',         views.order_detail,        name='order_detail'),
    path('order/<int:pk>/status/',  views.update_order_status, name='update_order_status'),
    path('menu/manage/',            views.menu_management,     name='menu_management'),

    # Guest portal
    path('menu/',                   views.guest_menu,          name='guest_menu'),
    path('order/',                  views.guest_place_order,   name='guest_place_order'),
    path('order/<int:pk>/track/',   views.guest_order_status,  name='guest_order_status'),
]
