# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    balance_qty = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'item_code', 'description', 'category', 'unit', 'opening_stock', 'received_qty', 'issued_qty', 'unit_cost', 'reorder_level', 'location', 'notes', 'created_at', 'updated_at', 'created_by', 'updated_by', 'balance_qty', 'total_value', 'stock_status']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'item_code']
