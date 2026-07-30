# -*- coding: utf-8 -*-
from django.utils.html import strip_tags
from rest_framework import serializers
from .models import CurrentAsset

def sanitize_html(value):
    if value and isinstance(value, str):
        return strip_tags(value)
    return value

class CurrentAssetSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=200)
    notes = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = CurrentAsset
        fields = ['id', 'asset_id', 'description', 'category', 'department',
                  'date_recorded', 'value', 'location', 'status', 'notes',
                  'created_at', 'updated_at', 'created_by', 'updated_by']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                            'updated_by', 'asset_id']

    def validate_description(self, value):
        return sanitize_html(value)

    def validate_notes(self, value):
        return sanitize_html(value)
