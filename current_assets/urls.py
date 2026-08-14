# -*- coding: utf-8 -*-
from django.urls import path
from .views import (
    current_asset_list, current_asset_create, current_asset_update,
    current_asset_delete, current_asset_bulk_delete, current_asset_bulk_edit,
    current_asset_export,
)

app_name = 'current_assets'
urlpatterns = [
    path('', current_asset_list, name='current_asset_list'),
    path('add/', current_asset_create, name='current_asset_create'),
    path('edit/<int:pk>/', current_asset_update, name='current_asset_update'),
    path('delete/<int:pk>/', current_asset_delete, name='current_asset_delete'),
    path('delete/bulk/', current_asset_bulk_delete, name='current_asset_bulk_delete'),
    path('edit/bulk/', current_asset_bulk_edit, name='current_asset_bulk_edit'),
    path('export/', current_asset_export, name='current_asset_export'),
]
