from django.urls import path
from . import views

app_name = 'requests_app'

urlpatterns = [
    # Staff views
    path('',                                views.request_list,            name='request_list'),
    path('reception/',                      views.reception_dashboard,     name='reception_dashboard'),
    path('department/',                     views.department_dashboard,    name='department_dashboard'),
    path('<int:pk>/',                       views.request_detail,          name='request_detail'),
    path('<int:pk>/assign/',                views.assign_request,          name='assign_request'),
    path('<int:pk>/status/',                views.update_request_status,   name='update_status'),
    path('<int:pk>/message/',               views.send_message,            name='send_message'),
    path('<int:pk>/messages/json/',         views.request_messages_json,   name='messages_json'),

    # Guest portal views
    path('submit/',                         views.guest_submit_request,    name='guest_submit_request'),
    path('status/<int:pk>/',               views.guest_request_status,    name='guest_request_status'),
    path('status/<int:pk>/message/',       views.guest_send_message,      name='guest_send_message'),
]
