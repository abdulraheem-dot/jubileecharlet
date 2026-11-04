from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Experience
from .serializers import ExperienceSerializer


class ExperienceListView(generics.ListAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [AllowAny]
    queryset = Experience.objects.filter(is_active=True)
    pagination_class = None


class ExperienceDetailView(generics.RetrieveAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [AllowAny]
    queryset = Experience.objects.filter(is_active=True)
    lookup_field = 'slug'
