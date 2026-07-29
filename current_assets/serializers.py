# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import CurrentAsset

class CurrentAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentAsset
        fields = ['id', 'asset_id', 'description', 'category', 'department', 'date_recorded', 'value', 'location', 'status', 'notes', 'created_at', 'updated_at', 'created_by', 'updated_by']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'asset_id']
