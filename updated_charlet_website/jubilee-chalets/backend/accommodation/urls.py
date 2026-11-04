from django.urls import path
from . import views

urlpatterns = [
    path('', views.RoomListView.as_view(), name='room-list'),
    path('categories/', views.RoomCategoryListView.as_view(), name='room-categories'),
    path('availability/', views.check_availability, name='room-availability'),
    path('<slug:slug>/', views.RoomDetailView.as_view(), name='room-detail'),
]
