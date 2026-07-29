# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import FixedAsset, DepreciationSchedule

class DepreciationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepreciationSchedule
        fields = ['id', 'asset', 'year_number', 'start_date', 'end_date', 'opening_nbv', 'annual_depreciation', 'accumulated_depreciation', 'closing_nbv']
        read_only_fields = ['id']


class FixedAssetSerializer(serializers.ModelSerializer):
    depreciation_schedules = DepreciationScheduleSerializer(many=True, read_only=True)
    annual_depreciation = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    accumulated_depreciation = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    net_book_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = FixedAsset
        fields = ['id', 'asset_id', 'asset_name', 'category', 'department', 'location', 'serial_number', 'supplier', 'purchase_date', 'purchase_cost', 'useful_life', 'salvage_value', 'depreciation_method', 'status', 'assigned_to', 'condition', 'disposal_date', 'notes', 'created_at', 'updated_at', 'created_by', 'updated_by', 'annual_depreciation', 'accumulated_depreciation', 'net_book_value', 'depreciation_schedules']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'asset_id']
