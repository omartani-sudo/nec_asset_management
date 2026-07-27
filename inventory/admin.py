# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'description', 'category', 'balance_qty', 'unit_cost', 'total_value', 'stock_status')
    list_filter = ('category', 'location')
    search_fields = ('item_code', 'description')
