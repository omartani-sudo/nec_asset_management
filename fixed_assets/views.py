# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.http import JsonResponse
from .models import FixedAsset, DepreciationSchedule
from lists.models import Category, Department, Location, Status
from .forms import FixedAssetForm, ExcelUploadForm
from core.decorators import admin_required

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
            messages.success(request, f'Fixed asset "{asset.asset_id}" created successfully.')
            return redirect('fixed_assets:fixed_asset_list')
    else:
        form = FixedAssetForm()
    next_serial = FixedAsset.objects.count() + 1
    return render(request, 'fixed_assets/form.html', {
        'form': form,
        'title': 'Add Fixed Asset',
        'next_serial': next_serial,
    })

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
    return render(request, 'fixed_assets/form.html', {
        'form': form,
        'title': 'Edit Fixed Asset',
        'asset_id': asset.asset_id,
    })

@login_required
def fixed_asset_detail(request, pk):
    asset = get_object_or_404(FixedAsset.objects.select_related('category', 'department', 'location', 'status', 'assigned_to'), pk=pk)
    schedules = asset.depreciation_schedules.all()
    context = {'asset': asset, 'schedules': schedules}
    return render(request, 'fixed_assets/detail.html', context)

@login_required
@admin_required('fixed_assets:fixed_asset_list')
def fixed_asset_delete(request, pk):
    asset = get_object_or_404(FixedAsset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Fixed asset deleted.')
        return redirect('fixed_assets:fixed_asset_list')
    return render(request, 'fixed_assets/delete.html', {'asset': asset})

@login_required
@admin_required('fixed_assets:fixed_asset_list')
def fixed_asset_bulk_delete(request):
    """Delete multiple fixed assets selected via checkboxes on the list page.

    Flow: POST with asset_ids from the list page -> confirmation page listing
    the assets -> POST with confirm=1 -> deletes all in one transaction.
    """
    if request.method == 'POST':
        ids = request.POST.getlist('asset_ids')
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect('fixed_assets:fixed_asset_list')
        assets = FixedAsset.objects.filter(pk__in=ids)
        if 'confirm' in request.POST:
            count = assets.count()
            with transaction.atomic():
                assets.delete()
            messages.success(request, f'{count} fixed asset{"s" if count != 1 else ""} deleted.')
            return redirect('fixed_assets:fixed_asset_list')
        return render(request, 'fixed_assets/bulk_delete.html', {
            'assets': assets,
            'asset_ids': ids,
        })
    return redirect('fixed_assets:fixed_asset_list')

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


@login_required
def upload_excel(request):
    from core.excel_importer import import_lists, import_fixed_assets

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                lists_result = import_lists(excel_file)
                excel_file.seek(0)  # reset for second read
                assets_result = import_fixed_assets(excel_file)

                imported = assets_result.get('imported', 0)
                skipped = assets_result.get('skipped', 0)
                errors = assets_result.get('errors', [])

                messages.success(
                    request,
                    f'Import complete! {imported} fixed assets imported, {skipped} skipped.'
                )
                # Show first few errors
                for aid, name, err in errors[:5]:
                    messages.warning(request, f'Failed: {aid} - {name}: {err}')

                return redirect('fixed_assets:fixed_asset_list')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.exception('Excel import failed for user %s', request.user.username)
                messages.error(request, 'Import failed due to an internal error. Please check that the file is a valid NEC Asset Registration Excel file.')
                return redirect('fixed_assets:upload_excel')
    else:
        form = ExcelUploadForm()

    return render(request, 'fixed_assets/upload_excel.html', {
        'form': form,
        'title': 'Import Excel Data',
    })
