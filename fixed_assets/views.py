# -*- coding: utf-8 -*-
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .models import FixedAsset, DepreciationSchedule
from lists.models import Category, Department, Location, Status
from .forms import FixedAssetForm, ExcelUploadForm, FixedAssetBulkEditForm
from core.decorators import admin_required, finance_admin_required
from core.filters import query_string, apply_sort, page_range
from core.models import AuditLog

FIXED_SORT_MAP = {
    'asset_id': 'asset_id',
    'name': 'asset_name',
    'purchase_date': 'purchase_date',
    'cost': 'purchase_cost',
    'serial': 'serial_number',
    'condition': 'condition',
}


def _filter_fixed_assets(params):
    """Build the filtered/sorted FixedAsset queryset from GET params."""
    qs = FixedAsset.objects.select_related(
        'category', 'department', 'location', 'status', 'assigned_to'
    ).all()
    q = params.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(asset_id__icontains=q) | Q(asset_name__icontains=q)
            | Q(serial_number__icontains=q) | Q(supplier__icontains=q)
        )
    for key, field in (
        ('category', 'category_id'), ('department', 'department_id'),
        ('location', 'location_id'), ('status', 'status_id'),
    ):
        val = params.get(key, '')
        if val and val.isdigit():
            qs = qs.filter(**{field: val})
    condition = params.get('condition', '')
    if condition:
        qs = qs.filter(condition=condition)
    for key, lookup in (('date_from', 'purchase_date__gte'), ('date_to', 'purchase_date__lte')):
        val = params.get(key, '')
        if val:
            try:
                qs = qs.filter(**{lookup: datetime.strptime(val, '%Y-%m-%d').date()})
            except ValueError:
                pass  # ignore malformed dates
    return apply_sort(qs, params, FIXED_SORT_MAP, FixedAsset._meta.ordering)


@login_required
def fixed_asset_list(request):
    qs = _filter_fixed_assets(request.GET)
    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', '1'))
    context = {
        'assets': page_obj,
        'page_obj': page_obj,
        'query_string': query_string(request.GET),
        'page_range': page_range(page_obj),
        'query_string_nosort': query_string(request.GET, exclude=('page', 'sort', 'dir')),
        'categories': Category.objects.all(),
        'departments': Department.objects.all(),
        'locations': Location.objects.all(),
        'statuses': Status.objects.all(),
        'condition_choices': FixedAsset.CONDITION_CHOICES,
        'sort_map': FIXED_SORT_MAP,
        'can_edit': request.user.role in ('admin', 'finance'),
        'can_delete': request.user.role == 'admin',
    }
    return render(request, 'fixed_assets/list.html', context)

@login_required
@finance_admin_required('fixed_assets:fixed_asset_list')
def fixed_asset_create(request):
    if request.method == 'POST':
        form = FixedAssetForm(request.POST, request.FILES)
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
@finance_admin_required('fixed_assets:fixed_asset_list')
def fixed_asset_update(request, pk):
    asset = get_object_or_404(FixedAsset, pk=pk)
    if request.method == 'POST':
        form = FixedAssetForm(request.POST, request.FILES, instance=asset)
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
        next_qs = request.POST.get('next_qs', '')
        list_url = 'fixed_assets:fixed_asset_list'
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect(list_url)
        assets = FixedAsset.objects.filter(pk__in=ids)
        if 'confirm' in request.POST:
            count = assets.count()
            ids_str = list(assets.values_list('pk', flat=True))
            with transaction.atomic():
                assets.delete()
            AuditLog.objects.create(
                user=request.user, action='bulk_delete', model_name='FixedAsset',
                object_repr=f'{count} fixed assets', details={'ids': ids_str, 'count': count},
            )
            messages.success(request, f'{count} fixed asset{"s" if count != 1 else ""} deleted.')
            return redirect(list_url + ('?' + next_qs if next_qs else ''))
        return render(request, 'fixed_assets/bulk_delete.html', {
            'assets': assets,
            'asset_ids': ids,
            'next_qs': next_qs,
        })
    return redirect('fixed_assets:fixed_asset_list')


@login_required
@finance_admin_required('fixed_assets:fixed_asset_list')
def fixed_asset_bulk_edit(request):
    """Edit shared fields on multiple fixed assets selected via checkboxes."""
    list_url = 'fixed_assets:fixed_asset_list'
    if request.method == 'POST':
        ids = request.POST.getlist('asset_ids')
        next_qs = request.POST.get('next_qs', '')
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect(list_url)
        assets = FixedAsset.objects.filter(pk__in=ids)
        if 'apply' in request.POST:
            form = FixedAssetBulkEditForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                changes = {}
                if data.get('status'):
                    changes['status'] = data['status']
                if data.get('department'):
                    changes['department'] = data['department']
                if data.get('location'):
                    changes['location'] = data['location']
                if data.get('condition'):
                    changes['condition'] = data['condition']
                if data.get('assigned_to'):
                    changes['assigned_to'] = data['assigned_to']
                if data.get('dispose'):
                    disposed_status, _ = Status.objects.get_or_create(name='Disposed')
                    changes['status'] = disposed_status
                    changes['disposal_date'] = timezone.localdate()
                if changes:
                    count = 0
                    with transaction.atomic():
                        for asset in assets:
                            for field, value in changes.items():
                                setattr(asset, field, value)
                            asset.updated_by = request.user
                            asset.save()
                            count += 1
                    AuditLog.objects.create(
                        user=request.user, action='bulk_edit', model_name='FixedAsset',
                        object_repr=f'{count} fixed assets updated',
                        details={'ids': list(assets.values_list('pk', flat=True)),
                                 'fields': list(changes), 'count': count},
                    )
                    messages.success(request, f'{count} fixed asset{"s" if count != 1 else ""} updated.')
                else:
                    messages.info(request, 'No changes selected — nothing was updated.')
                return redirect(list_url + ('?' + next_qs if next_qs else ''))
        else:
            form = FixedAssetBulkEditForm()
        return render(request, 'fixed_assets/bulk_edit.html', {
            'assets': assets,
            'asset_ids': ids,
            'form': form,
            'next_qs': next_qs,
        })
    return redirect(list_url)


@login_required
@finance_admin_required('fixed_assets:fixed_asset_list')
def fixed_asset_dispose(request, pk):
    """Mark a fixed asset as disposed (sets status + disposal date)."""
    asset = get_object_or_404(FixedAsset, pk=pk)
    if request.method == 'POST':
        if asset.disposal_date:
            messages.info(request, f'{asset.asset_id} is already disposed.')
        else:
            disposed_status, _ = Status.objects.get_or_create(name='Disposed')
            asset.status = disposed_status
            asset.disposal_date = timezone.localdate()
            asset.updated_by = request.user
            asset.save()
            messages.success(request, f'{asset.asset_id} marked as disposed on {asset.disposal_date}.')
        return redirect('fixed_assets:fixed_asset_detail', pk=pk)
    return redirect('fixed_assets:fixed_asset_detail', pk=pk)


@login_required
def fixed_asset_print_qr(request):
    """Render a printable QR-label sheet for the selected assets."""
    list_url = 'fixed_assets:fixed_asset_list'
    if request.method == 'POST':
        ids = request.POST.getlist('asset_ids')
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect(list_url)
        assets = FixedAsset.objects.filter(pk__in=ids).select_related('location')
        labels = [{
            'asset_id': a.asset_id,
            'name': a.asset_name,
            'location': a.location.name if a.location else '',
            'url': request.build_absolute_uri(
                reverse('fixed_assets:fixed_asset_detail', args=[a.pk])
            ),
        } for a in assets]
        return render(request, 'fixed_assets/qr_sheet.html', {'labels': labels})
    return redirect(list_url)

@login_required
def fixed_asset_export(request):
    """Export the currently filtered fixed-assets list to Excel."""
    import pandas as pd
    from reports.views import export_to_excel
    qs = _filter_fixed_assets(request.GET)
    rows = [{
        'Asset ID': a.asset_id,
        'Name': a.asset_name,
        'Category': a.category.name,
        'Department': a.department.name,
        'Location': a.location.name,
        'Serial Number': a.serial_number,
        'Supplier': a.supplier,
        'Purchase Date': a.purchase_date,
        'Purchase Cost': float(a.purchase_cost),
        'Useful Life (yrs)': a.useful_life,
        'Salvage Value': float(a.salvage_value),
        'Depreciation Method': a.get_depreciation_method_display(),
        'Status': a.status.name,
        'Condition': a.get_condition_display(),
        'Assigned To': a.assigned_to.username if a.assigned_to else '',
        'Disposal Date': a.disposal_date or '',
        'Net Book Value': float(a.net_book_value()),
        'Notes': a.notes,
    } for a in qs]
    df = pd.DataFrame(rows)
    return export_to_excel(df, 'fixed_assets_export.xlsx')


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
