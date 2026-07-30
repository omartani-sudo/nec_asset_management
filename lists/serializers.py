# -*- coding: utf-8 -*-
from django.utils.html import strip_tags
from rest_framework import serializers
from .models import Category, Department, Location, Status, Unit


def sanitize_html(value):
    if value and isinstance(value, str):
        return strip_tags(value)
    return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return sanitize_html(value)

    def validate_description(self, value):
        return sanitize_html(value)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return sanitize_html(value)

    def validate_description(self, value):
        return sanitize_html(value)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return sanitize_html(value)

    def validate_description(self, value):
        return sanitize_html(value)


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return sanitize_html(value)

    def validate_description(self, value):
        return sanitize_html(value)


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return sanitize_html(value)

    def validate_description(self, value):
        return sanitize_html(value)
