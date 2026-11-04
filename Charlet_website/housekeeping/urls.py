from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('',                    views.dashboard,            name='dashboard'),
    path('task/<int:pk>/',      views.update_task,          name='update_task'),
    path('rooms/',              views.room_status_overview, name='room_status'),
]
