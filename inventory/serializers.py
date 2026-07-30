# -*- coding: utf-8 -*-
from django.utils.html import strip_tags
from rest_framework import serializers
from .models import InventoryItem

def sanitize_html(value):
    if value and isinstance(value, str):
        return strip_tags(value)
    return value

class InventoryItemSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=200)
    notes = serializers.CharField(allow_blank=True, required=False)
    balance_qty = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'item_code', 'description', 'category', 'unit',
                  'opening_stock', 'received_qty', 'issued_qty', 'unit_cost',
                  'reorder_level', 'location', 'notes',
                  'created_at', 'updated_at', 'created_by', 'updated_by',
                  'balance_qty', 'total_value', 'stock_status']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                            'updated_by', 'item_code']

    def validate_description(self, value):
        return sanitize_html(value)

    def validate_notes(self, value):
        return sanitize_html(value)
