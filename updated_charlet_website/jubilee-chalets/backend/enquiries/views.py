from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from .models import ContactEnquiry, Testimonial, FAQ, NewsletterSubscription
from .serializers import (
    ContactEnquirySerializer, TestimonialSerializer,
    FAQSerializer, NewsletterSubscriptionSerializer,
)


class ContactEnquiryCreateView(generics.CreateAPIView):
    serializer_class = ContactEnquirySerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Your message has been received. We\'ll respond within 24 hours.'},
            status=status.HTTP_201_CREATED,
        )


class TestimonialListView(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    queryset = Testimonial.objects.filter(is_approved=True)
    pagination_class = None


class FAQListView(generics.ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    pagination_class = None

    def get_queryset(self):
        return FAQ.objects.filter(is_active=True)


class NewsletterSubscribeView(generics.CreateAPIView):
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Thank you for subscribing!'}, status=status.HTTP_201_CREATED)
