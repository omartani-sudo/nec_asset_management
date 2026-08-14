# -*- coding: utf-8 -*-
from django.urls import path
from .views import (
    inventory_list, inventory_create, inventory_update, inventory_delete,
    inventory_bulk_delete, inventory_bulk_edit, reorder_list,
)

app_name = 'inventory'
urlpatterns = [
    path('', inventory_list, name='inventory_list'),
    path('add/', inventory_create, name='inventory_create'),
    path('edit/<int:pk>/', inventory_update, name='inventory_update'),
    path('delete/<int:pk>/', inventory_delete, name='inventory_delete'),
    path('delete/bulk/', inventory_bulk_delete, name='inventory_bulk_delete'),
    path('edit/bulk/', inventory_bulk_edit, name='inventory_bulk_edit'),
    path('reorder/', reorder_list, name='reorder_list'),
]
