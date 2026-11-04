from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    # Staff views
    path('',                    views.guest_list,     name='guest_list'),
    path('<int:pk>/',           views.guest_detail,   name='guest_detail'),
    path('checkin/',            views.guest_checkin,  name='guest_checkin'),
    path('<int:pk>/checkout/',  views.guest_checkout, name='guest_checkout'),

    # Guest portal views
    path('portal/',             views.portal_entry,        name='portal_entry'),
    path('portal/home/',        views.portal_home,         name='portal_home'),
    path('portal/logout/',      views.portal_logout,       name='portal_logout'),
    path('room/<str:token>/',   views.portal_room_access,  name='portal_room_access'),
]
