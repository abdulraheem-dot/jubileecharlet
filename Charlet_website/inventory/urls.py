from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('',                    views.item_list,       name='list'),
    path('new/',                views.create_item,     name='create'),
    path('<int:pk>/update/',    views.update_quantity, name='update_quantity'),
]
