# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from .models import FixedAsset
from lists.models import Category, Department, Location, Status

User = get_user_model()


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select NEC Excel File',
        help_text='Upload the NEC Asset Registration Excel file (.xlsx format, max 10MB)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'}),
        max_length=255,
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')
        if excel_file:
            # Validate extension
            allowed_extensions = ('.xlsx',)
            if not excel_file.name.lower().endswith(allowed_extensions):
                raise forms.ValidationError(
                    'Invalid file type. Only .xlsx files are accepted.'
                )
            # Validate size (10 MB limit, compressed)
            max_size = 10 * 1024 * 1024
            if excel_file.size > max_size:
                raise forms.ValidationError(
                    'File too large. Maximum size is 10 MB.'
                )
            # Validate MIME type
            allowed_mimes = (
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/octet-stream',  # Some browsers send this for .xlsx
            )
            if hasattr(excel_file, 'content_type') and excel_file.content_type:
                if excel_file.content_type not in allowed_mimes:
                    raise forms.ValidationError(
                        'Invalid file type. Only .xlsx files are accepted.'
                    )
            # Zip-bomb guard: cap total uncompressed size before pandas reads it
            try:
                import zipfile
                excel_file.seek(0)
                with zipfile.ZipFile(excel_file) as zf:
                    total_uncompressed = sum(info.file_size for info in zf.infolist())
                if total_uncompressed > 100 * 1024 * 1024:
                    raise forms.ValidationError(
                        'File too large when decompressed. Maximum is 100 MB.'
                    )
                excel_file.seek(0)
            except zipfile.BadZipFile:
                raise forms.ValidationError(
                    'Invalid file. Not a valid .xlsx workbook.'
                )
        return excel_file


class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = ['asset_name', 'category', 'department', 'location', 'serial_number', 'supplier', 'purchase_date', 'purchase_cost', 'useful_life', 'salvage_value', 'depreciation_method', 'status', 'assigned_to', 'condition', 'disposal_date', 'photo', 'notes']
        widgets = {
            'asset_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to auto-generate'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'useful_life': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'salvage_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'depreciation_method': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'disposal_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Photo too large. Maximum size is 5 MB.')
        return photo


class FixedAssetBulkEditForm(forms.Form):
    """Change shared fields on many fixed assets at once. Empty = no-op."""
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
    condition = forms.ChoiceField(
        choices=[('', '-- No change --')] + list(FixedAsset.CONDITION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True), required=False,
        empty_label='-- No change --',
        widget=forms.Select(attrs={'class': 'form-select'}))
    dispose = forms.BooleanField(
        required=False, label='Mark as disposed (sets Disposed status and disposal date to today)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
