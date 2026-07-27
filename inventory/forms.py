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
