# -*- coding: utf-8 -*-
from django import forms
from .models import CurrentAsset
from lists.models import Category, Department, Location, Status

class CurrentAssetForm(forms.ModelForm):
    class Meta:
        model = CurrentAsset
        fields = ['description', 'category', 'department', 'date_recorded', 'value', 'location', 'status', 'notes']
        widgets = {
            'date_recorded': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
