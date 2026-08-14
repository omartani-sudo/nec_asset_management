# -*- coding: utf-8 -*-
from django import forms
from .models import CurrentAsset
from lists.models import Category, Department, Location, Status


class CurrentAssetBulkEditForm(forms.Form):
    """Change shared fields on many current assets at once. Empty = no-op."""
    status = forms.ModelChoiceField(
        queryset=Status.objects.all(), required=False,
        empty_label='-- No change --',
        widget=forms.Select(attrs={'class': 'form-select'}))
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), required=False,
        empty_label='-- No change --',
        widget=forms.Select(attrs={'class': 'form-select'}))
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(), required=False,
        empty_label='-- No change --',
        widget=forms.Select(attrs={'class': 'form-select'}))

class CurrentAssetForm(forms.ModelForm):
    class Meta:
        model = CurrentAsset
        fields = ['description', 'category', 'department', 'date_recorded', 'value', 'location', 'status', 'notes']
        widgets = {
            'date_recorded': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
