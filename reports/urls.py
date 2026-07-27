# -*- coding: utf-8 -*-
from django.urls import path
from .views import (
    reports_home, asset_status_report, fixed_assets_by_category,
    fixed_assets_by_department, inventory_summary, reorder_report,
    export_fixed_assets_category, export_fixed_assets_department,
    export_asset_status, export_inventory_summary, export_reorder_list,
)

app_name = 'reports'
urlpatterns = [
    path('', reports_home, name='reports_home'),
    path('asset-status/', asset_status_report, name='asset_status_report'),
    path('fixed-assets/by-category/', fixed_assets_by_category, name='fixed_assets_by_category'),
    path('fixed-assets/by-department/', fixed_assets_by_department, name='fixed_assets_by_department'),
    path('inventory-summary/', inventory_summary, name='inventory_summary'),
    path('reorder-list/', reorder_report, name='reorder_report'),
    path('export/fixed-assets/by-category/', export_fixed_assets_category, name='export_fixed_assets_category'),
    path('export/fixed-assets/by-department/', export_fixed_assets_department, name='export_fixed_assets_department'),
    path('export/asset-status/', export_asset_status, name='export_asset_status'),
    path('export/inventory-summary/', export_inventory_summary, name='export_inventory_summary'),
    path('export/reorder-list/', export_reorder_list, name='export_reorder_list'),
]
