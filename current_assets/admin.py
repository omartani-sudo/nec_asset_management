# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import CurrentAsset

@admin.register(CurrentAsset)
class CurrentAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'description', 'category', 'department', 'date_recorded', 'value', 'status')
    list_filter = ('category', 'department', 'status')
    search_fields = ('asset_id', 'description')
    date_hierarchy = 'date_recorded'
