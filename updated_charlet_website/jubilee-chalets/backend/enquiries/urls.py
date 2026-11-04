from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.ContactEnquiryCreateView.as_view(), name='contact'),
    path('testimonials/', views.TestimonialListView.as_view(), name='testimonials'),
    path('faqs/', views.FAQListView.as_view(), name='faqs'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
]
