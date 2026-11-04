from django.urls import path
from . import views

urlpatterns = [
    path('venues/', views.EventVenueListView.as_view(), name='event-venues'),
    path('enquiries/', views.EventEnquiryCreateView.as_view(), name='event-enquiries'),
]
