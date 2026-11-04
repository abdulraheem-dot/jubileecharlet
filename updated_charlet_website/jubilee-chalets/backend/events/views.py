from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import EventVenue, EventEnquiry
from .serializers import EventVenueSerializer, EventEnquirySerializer


class EventVenueListView(generics.ListAPIView):
    serializer_class = EventVenueSerializer
    permission_classes = [AllowAny]
    queryset = EventVenue.objects.filter(is_active=True)
    pagination_class = None


class EventEnquiryCreateView(generics.CreateAPIView):
    serializer_class = EventEnquirySerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Your event enquiry has been submitted. Our team will be in touch shortly.'},
            status=status.HTTP_201_CREATED,
        )
