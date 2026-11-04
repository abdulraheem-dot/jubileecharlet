from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('',                    views.room_list,          name='room_list'),
    path('new/',                views.room_create,         name='room_create'),
    path('<int:pk>/',           views.room_detail,         name='room_detail'),
    path('<int:pk>/edit/',      views.room_edit,           name='room_edit'),
    path('<int:pk>/qr/',        views.room_qr,             name='room_qr'),
    path('<int:pk>/status/',    views.update_room_status,  name='update_status'),
]
