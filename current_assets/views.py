# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CurrentAsset
from lists.models import Category, Department, Location, Status
from .forms import CurrentAssetForm

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
def current_asset_delete(request, pk):
    asset = get_object_or_404(CurrentAsset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Current asset deleted.')
        return redirect('current_asset_list')
    return render(request, 'current_assets/delete.html', {'asset': asset})
