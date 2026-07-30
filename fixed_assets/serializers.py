# -*- coding: utf-8 -*-
from django.utils.html import strip_tags
from rest_framework import serializers
from .models import FixedAsset, DepreciationSchedule


def sanitize_html(value):
    """Strip HTML tags to prevent stored XSS. Django templates auto-escape,
    but API consumers might not. Defense in depth."""
    if value and isinstance(value, str):
        return strip_tags(value)
    return value


class DepreciationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepreciationSchedule
        fields = ['id', 'asset', 'year_number', 'start_date', 'end_date',
                  'opening_nbv', 'annual_depreciation', 'accumulated_depreciation',
                  'closing_nbv']
        read_only_fields = ['id']


class FixedAssetSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(max_length=200)
    serial_number = serializers.CharField(max_length=100, allow_blank=True, required=False)
    supplier = serializers.CharField(max_length=200, allow_blank=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)
    depreciation_schedules = DepreciationScheduleSerializer(many=True, read_only=True)
    annual_depreciation = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    accumulated_depreciation = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    net_book_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = FixedAsset
        fields = ['id', 'asset_id', 'asset_name', 'category', 'department', 'location',
                  'serial_number', 'supplier', 'purchase_date', 'purchase_cost',
                  'useful_life', 'salvage_value', 'depreciation_method', 'status',
                  'assigned_to', 'condition', 'disposal_date', 'notes',
                  'created_at', 'updated_at', 'created_by', 'updated_by',
                  'annual_depreciation', 'accumulated_depreciation', 'net_book_value',
                  'depreciation_schedules']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                            'updated_by', 'asset_id']

    def validate_asset_name(self, value):
        return sanitize_html(value)

    def validate_serial_number(self, value):
        return sanitize_html(value)

    def validate_supplier(self, value):
        return sanitize_html(value)

    def validate_notes(self, value):
        return sanitize_html(value)
