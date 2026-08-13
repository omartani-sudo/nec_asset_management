# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import CurrentAsset
from lists.models import Category, Department, Location, Status
from .forms import CurrentAssetForm
from core.decorators import admin_required

@login_required
def current_asset_list(request):
    assets = CurrentAsset.objects.select_related('category', 'department', 'location', 'status').all()
    return render(request, 'current_assets/list.html', {'assets': assets})

@login_required
def current_asset_create(request):
    if request.method == 'POST':
        form = CurrentAssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.created_by = request.user
            asset.updated_by = request.user
            asset.save()
            messages.success(request, 'Current asset created successfully.')
            return redirect('current_assets:current_asset_list')
    else:
        form = CurrentAssetForm()
    return render(request, 'current_assets/form.html', {'form': form, 'title': 'Add Current Asset'})

@login_required
def current_asset_update(request, pk):
    asset = get_object_or_404(CurrentAsset, pk=pk)
    if request.method == 'POST':
        form = CurrentAssetForm(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.updated_by = request.user
            asset.save()
            messages.success(request, 'Current asset updated successfully.')
            return redirect('current_assets:current_asset_list')
    else:
        form = CurrentAssetForm(instance=asset)
    return render(request, 'current_assets/form.html', {'form': form, 'title': 'Edit Current Asset'})

@login_required
@admin_required('current_assets:current_asset_list')
def current_asset_delete(request, pk):
    asset = get_object_or_404(CurrentAsset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Current asset deleted.')
        return redirect('current_asset_list')
    return render(request, 'current_assets/delete.html', {'asset': asset})

@login_required
@admin_required('current_assets:current_asset_list')
def current_asset_bulk_delete(request):
    """Delete multiple current assets selected via checkboxes on the list page."""
    if request.method == 'POST':
        ids = request.POST.getlist('asset_ids')
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect('current_assets:current_asset_list')
        assets = CurrentAsset.objects.filter(pk__in=ids)
        if 'confirm' in request.POST:
            count = assets.count()
            with transaction.atomic():
                assets.delete()
            messages.success(request, f'{count} current asset{"s" if count != 1 else ""} deleted.')
            return redirect('current_assets:current_asset_list')
        return render(request, 'current_assets/bulk_delete.html', {
            'assets': assets,
            'asset_ids': ids,
        })
    return redirect('current_assets:current_asset_list')
