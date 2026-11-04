from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('',                    views.dashboard,      name='dashboard'),
    path('new/',                views.create_record,  name='create_record'),
    path('<int:pk>/',           views.record_detail,  name='record_detail'),
    path('<int:pk>/update/',    views.update_record,  name='update_record'),
]
