from rest_framework import generics
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import MenuCategory, MenuItem
from .serializers import MenuCategorySerializer, MenuItemSerializer


class MenuCategoryListView(generics.ListAPIView):
    serializer_class = MenuCategorySerializer
    permission_classes = [AllowAny]
    queryset = MenuCategory.objects.all()
    pagination_class = None


class MenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_available']
    pagination_class = None

    def get_queryset(self):
        return MenuItem.objects.select_related('category').all()
