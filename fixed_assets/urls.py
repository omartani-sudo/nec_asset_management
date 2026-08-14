# -*- coding: utf-8 -*-
from django.urls import path
from .views import (
    fixed_asset_list, fixed_asset_create, fixed_asset_update,
    fixed_asset_detail, fixed_asset_delete, fixed_asset_bulk_delete,
    fixed_asset_bulk_edit, fixed_asset_export, fixed_asset_print_qr,
    fixed_asset_dispose, fixed_asset_summary, fixed_assets_by_department,
    upload_excel,
)

app_name = 'fixed_assets'
urlpatterns = [
    path('', fixed_asset_list, name='fixed_asset_list'),
    path('add/', fixed_asset_create, name='fixed_asset_create'),
    path('edit/<int:pk>/', fixed_asset_update, name='fixed_asset_update'),
    path('view/<int:pk>/', fixed_asset_detail, name='fixed_asset_detail'),
    path('delete/<int:pk>/', fixed_asset_delete, name='fixed_asset_delete'),
    path('delete/bulk/', fixed_asset_bulk_delete, name='fixed_asset_bulk_delete'),
    path('edit/bulk/', fixed_asset_bulk_edit, name='fixed_asset_bulk_edit'),
    path('export/', fixed_asset_export, name='fixed_asset_export'),
    path('print-qr/', fixed_asset_print_qr, name='fixed_asset_print_qr'),
    path('dispose/<int:pk>/', fixed_asset_dispose, name='fixed_asset_dispose'),
    path('reports/by-category/', fixed_asset_summary, name='fixed_asset_summary'),
    path('reports/by-department/', fixed_assets_by_department, name='fixed_assets_by_department'),
    path('upload-excel/', upload_excel, name='upload_excel'),
]
