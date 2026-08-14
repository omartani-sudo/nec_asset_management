# -*- coding: utf-8 -*-
from django import forms
from .models import InventoryItem
from lists.models import Category, Unit, Location

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['description', 'category', 'unit', 'opening_stock', 'received_qty', 'issued_qty', 'unit_cost', 'reorder_level', 'location', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class InventoryItemBulkEditForm(forms.Form):
    """Change shared fields on many inventory items at once. Empty = no-op."""
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(), required=False,
        empty_label='-- No change --',
        widget=forms.Select(attrs={'class': 'form-select'}))
    reorder_level = forms.IntegerField(
        required=False, min_value=0,
        label='Reorder level (leave blank for no change)',
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
