# -*- coding: utf-8 -*-
from django.urls import path
from .views import (
    inventory_list, inventory_create, inventory_update, inventory_delete, reorder_list,
)

app_name = 'inventory'
urlpatterns = [
    path('', inventory_list, name='inventory_list'),
    path('add/', inventory_create, name='inventory_create'),
    path('edit/<int:pk>/', inventory_update, name='inventory_update'),
    path('delete/<int:pk>/', inventory_delete, name='inventory_delete'),
    path('reorder/', reorder_list, name='reorder_list'),
]
