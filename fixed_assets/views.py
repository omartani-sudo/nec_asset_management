# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import FixedAsset, DepreciationSchedule
from lists.models import Category, Department, Location, Status
from .forms import FixedAssetForm

@login_required
def fixed_asset_list(request):
    assets = FixedAsset.objects.select_related('category', 'department', 'location', 'status', 'assigned_to').all()
    return render(request, 'fixed_assets/list.html', {'assets': assets})

@login_required
def fixed_asset_create(request):
    if request.method == 'POST':
        form = FixedAssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.created_by = request.user
            asset.updated_by = request.user
            asset.save()
            asset.generate_asset_id()
            asset.save(update_fields=['asset_id'])
            messages.success(request, 'Fixed asset created successfully.')
            return redirect('fixed_assets:fixed_asset_list')
    else:
        form = FixedAssetForm()
    return render(request, 'fixed_assets/form.html', {'form': form, 'title': 'Add Fixed Asset'})

@login_required
def fixed_asset_update(request, pk):
    asset = get_object_or_404(FixedAsset, pk=pk)
    if request.method == 'POST':
        form = FixedAssetForm(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.updated_by = request.user
            asset.save()
            messages.success(request, 'Fixed asset updated successfully.')
            return redirect('fixed_assets:fixed_asset_list')
    else:
        form = FixedAssetForm(instance=asset)
    return render(request, 'fixed_assets/form.html', {'form': form, 'title': 'Edit Fixed Asset'})

@login_required
def fixed_asset_detail(request, pk):
    asset = get_object_or_404(FixedAsset.objects.select_related('category', 'department', 'location', 'status', 'assigned_to'), pk=pk)
    schedules = asset.depreciation_schedules.all()
    context = {'asset': asset, 'schedules': schedules}
    return render(request, 'fixed_assets/detail.html', context)

@login_required
def fixed_asset_delete(request, pk):
    asset = get_object_or_404(FixedAsset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Fixed asset deleted.')
        return redirect('fixed_assets:fixed_asset_list')
    return render(request, 'fixed_assets/delete.html', {'asset': asset})

@login_required
def fixed_asset_summary(request):
    data = FixedAsset.objects.values('category__name').annotate(count=Count('id'), total_cost=Sum('purchase_cost'), total_nbv=Sum('purchase_cost'))
    context = {'data': data, 'title': 'Fixed Assets by Category'}
    return render(request, 'reports/fixed_assets_summary.html', context)

@login_required
def fixed_assets_by_department(request):
    data = FixedAsset.objects.values('department__name').annotate(count=Count('id'), total_cost=Sum('purchase_cost'), total_nbv=Sum('purchase_cost'))
    context = {'data': data, 'title': 'Fixed Assets by Department'}
    return render(request, 'reports/fixed_assets_summary.html', context)
