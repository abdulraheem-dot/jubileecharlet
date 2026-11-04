from rest_framework import generics
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import GalleryImage
from .serializers import GalleryImageSerializer


class GalleryListView(generics.ListAPIView):
    serializer_class = GalleryImageSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    pagination_class = None

    def get_queryset(self):
        return GalleryImage.objects.filter(is_active=True)
