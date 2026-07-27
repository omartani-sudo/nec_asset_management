# -*- coding: utf-8 -*-
from django import forms
from .models import FixedAsset
from lists.models import Category, Department, Location, Status

class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = ['asset_name', 'category', 'department', 'location', 'serial_number', 'supplier', 'purchase_date', 'purchase_cost', 'useful_life', 'salvage_value', 'depreciation_method', 'status', 'assigned_to', 'condition', 'disposal_date', 'notes']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'disposal_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
