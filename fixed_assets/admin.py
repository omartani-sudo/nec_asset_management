# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import FixedAsset, DepreciationSchedule

@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'asset_name', 'category', 'department', 'purchase_date', 'purchase_cost', 'depreciation_method', 'status', 'net_book_value')
    list_filter = ('category', 'department', 'status', 'depreciation_method')
    search_fields = ('asset_id', 'asset_name', 'serial_number')
    date_hierarchy = 'purchase_date'

@admin.register(DepreciationSchedule)
class DepreciationScheduleAdmin(admin.ModelAdmin):
    list_display = ('asset', 'year_number', 'annual_depreciation', 'accumulated_depreciation', 'closing_nbv')
    list_filter = ('asset', 'year_number')
