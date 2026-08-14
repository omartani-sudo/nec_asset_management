# -*- coding: utf-8 -*-
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from .models import CurrentAsset
from lists.models import Category, Department, Location, Status
from .forms import CurrentAssetForm, CurrentAssetBulkEditForm
from core.decorators import admin_required, finance_admin_required
from core.filters import query_string, apply_sort, page_range
from core.models import AuditLog

CURRENT_SORT_MAP = {
    'asset_id': 'asset_id',
    'description': 'description',
    'date_recorded': 'date_recorded',
    'value': 'value',
}


def _filter_current_assets(params):
    """Build the filtered/sorted CurrentAsset queryset from GET params."""
    qs = CurrentAsset.objects.select_related(
        'category', 'department', 'location', 'status'
    ).all()
    q = params.get('q', '').strip()
    if q:
        qs = qs.filter(Q(asset_id__icontains=q) | Q(description__icontains=q))
    for key, field in (
        ('category', 'category_id'), ('department', 'department_id'),
        ('location', 'location_id'), ('status', 'status_id'),
    ):
        val = params.get(key, '')
        if val and val.isdigit():
            qs = qs.filter(**{field: val})
    for key, lookup in (('date_from', 'date_recorded__gte'), ('date_to', 'date_recorded__lte')):
        val = params.get(key, '')
        if val:
            try:
                qs = qs.filter(**{lookup: datetime.strptime(val, '%Y-%m-%d').date()})
            except ValueError:
                pass  # ignore malformed dates
    return apply_sort(qs, params, CURRENT_SORT_MAP, CurrentAsset._meta.ordering)


@login_required
def current_asset_list(request):
    qs = _filter_current_assets(request.GET)
    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', '1'))
    context = {
        'assets': page_obj,
        'page_obj': page_obj,
        'query_string': query_string(request.GET),
        'page_range': page_range(page_obj),
        'categories': Category.objects.all(),
        'departments': Department.objects.all(),
        'locations': Location.objects.all(),
        'statuses': Status.objects.all(),
        'sort_map': CURRENT_SORT_MAP,
        'can_edit': request.user.role in ('admin', 'finance'),
        'can_delete': request.user.role == 'admin',
    }
    return render(request, 'current_assets/list.html', context)

@login_required
@finance_admin_required('current_assets:current_asset_list')
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
@finance_admin_required('current_assets:current_asset_list')
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
def current_asset_export(request):
    """Export the currently filtered current-assets list to Excel."""
    import pandas as pd
    from reports.views import export_to_excel
    qs = _filter_current_assets(request.GET)
    rows = [{
        'Asset ID': a.asset_id,
        'Description': a.description,
        'Category': a.category.name,
        'Department': a.department.name,
        'Location': a.location.name,
        'Date Recorded': a.date_recorded,
        'Value': float(a.value),
        'Status': a.status.name,
        'Notes': a.notes,
    } for a in qs]
    df = pd.DataFrame(rows)
    return export_to_excel(df, 'current_assets_export.xlsx')


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
        next_qs = request.POST.get('next_qs', '')
        list_url = 'current_assets:current_asset_list'
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect(list_url)
        assets = CurrentAsset.objects.filter(pk__in=ids)
        if 'confirm' in request.POST:
            count = assets.count()
            ids_str = list(assets.values_list('pk', flat=True))
            with transaction.atomic():
                assets.delete()
            AuditLog.objects.create(
                user=request.user, action='bulk_delete', model_name='CurrentAsset',
                object_repr=f'{count} current assets', details={'ids': ids_str, 'count': count},
            )
            messages.success(request, f'{count} current asset{"s" if count != 1 else ""} deleted.')
            return redirect(list_url + ('?' + next_qs if next_qs else ''))
        return render(request, 'current_assets/bulk_delete.html', {
            'assets': assets,
            'asset_ids': ids,
            'next_qs': next_qs,
        })
    return redirect('current_assets:current_asset_list')


@login_required
@finance_admin_required('current_assets:current_asset_list')
def current_asset_bulk_edit(request):
    """Edit shared fields on multiple current assets selected via checkboxes."""
    list_url = 'current_assets:current_asset_list'
    if request.method == 'POST':
        ids = request.POST.getlist('asset_ids')
        next_qs = request.POST.get('next_qs', '')
        if not ids:
            messages.error(request, 'No assets selected.')
            return redirect(list_url)
        assets = CurrentAsset.objects.filter(pk__in=ids)
        if 'apply' in request.POST:
            form = CurrentAssetBulkEditForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                changes = {}
                if data.get('status'):
                    changes['status'] = data['status']
                if data.get('department'):
                    changes['department'] = data['department']
                if data.get('location'):
                    changes['location'] = data['location']
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
                        user=request.user, action='bulk_edit', model_name='CurrentAsset',
                        object_repr=f'{count} current assets updated',
                        details={'ids': list(assets.values_list('pk', flat=True)),
                                 'fields': list(changes), 'count': count},
                    )
                    messages.success(request, f'{count} current asset{"s" if count != 1 else ""} updated.')
                else:
                    messages.info(request, 'No changes selected — nothing was updated.')
                return redirect(list_url + ('?' + next_qs if next_qs else ''))
        else:
            form = CurrentAssetBulkEditForm()
        return render(request, 'current_assets/bulk_edit.html', {
            'assets': assets,
            'asset_ids': ids,
            'form': form,
            'next_qs': next_qs,
        })
    return redirect(list_url)
