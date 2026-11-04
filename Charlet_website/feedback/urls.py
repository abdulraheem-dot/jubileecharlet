from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('',                            views.feedback_list,    name='list'),
    path('request/<int:request_pk>/',   views.guest_feedback,   name='guest_feedback'),
    path('complaint/',                  views.guest_complaint,  name='guest_complaint'),
]
