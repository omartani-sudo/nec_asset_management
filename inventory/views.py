# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum, F, ExpressionWrapper, IntegerField
from .models import InventoryItem
from lists.models import Category, Location, Status, Unit
from .forms import InventoryItemForm, InventoryItemBulkEditForm
from core.decorators import admin_required, finance_admin_required
from core.filters import query_string, apply_sort, page_range
from core.models import AuditLog

INVENTORY_SORT_MAP = {
    'item_code': 'item_code',
    'description': 'description',
    'balance': 'balance',
    'unit_cost': 'unit_cost',
}


def _annotate_balance(qs):
    return qs.annotate(balance=ExpressionWrapper(
        F('opening_stock') + F('received_qty') - F('issued_qty'),
        output_field=IntegerField()
    ))


def _filter_inventory(params):
    """Build the filtered/sorted InventoryItem queryset from GET params."""
    qs = _annotate_balance(
        InventoryItem.objects.select_related('category', 'unit', 'location').all()
    )
    q = params.get('q', '').strip()
    if q:
        qs = qs.filter(Q(item_code__icontains=q) | Q(description__icontains=q))
    for key, field in (('category', 'category_id'), ('location', 'location_id')):
        val = params.get(key, '')
        if val and val.isdigit():
            qs = qs.filter(**{field: val})
    stock_status = params.get('stock_status', '')
    if stock_status == 'out':
        qs = qs.filter(balance=0)
    elif stock_status == 'reorder':
        qs = qs.filter(balance__lte=F('reorder_level'), balance__gt=0)
    elif stock_status == 'ok':
        qs = qs.filter(balance__gt=F('reorder_level'))
    return apply_sort(qs, params, INVENTORY_SORT_MAP, InventoryItem._meta.ordering)


@login_required
def inventory_list(request):
    qs = _filter_inventory(request.GET)
    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', '1'))
    context = {
        'items': page_obj,
        'page_obj': page_obj,
        'query_string': query_string(request.GET),
        'page_range': page_range(page_obj),
        'categories': Category.objects.all(),
        'locations': Location.objects.all(),
        'sort_map': INVENTORY_SORT_MAP,
        'can_edit': request.user.role in ('admin', 'finance'),
        'can_delete': request.user.role == 'admin',
    }
    return render(request, 'inventory/list.html', context)

@login_required
@finance_admin_required('inventory:inventory_list')
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.updated_by = request.user
            item.save()
            messages.success(request, 'Inventory item created successfully.')
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Add Inventory Item'})

@login_required
@finance_admin_required('inventory:inventory_list')
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.updated_by = request.user
            item.save()
            messages.success(request, 'Inventory item updated successfully.')
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Edit Inventory Item'})

@login_required
@admin_required('inventory:inventory_list')
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Inventory item deleted.')
        return redirect('inventory_list')
    return render(request, 'inventory/delete.html', {'item': item})

@login_required
@admin_required('inventory:inventory_list')
def inventory_bulk_delete(request):
    """Delete multiple inventory items selected via checkboxes on the list page."""
    if request.method == 'POST':
        ids = request.POST.getlist('item_ids')
        next_qs = request.POST.get('next_qs', '')
        list_url = 'inventory:inventory_list'
        if not ids:
            messages.error(request, 'No items selected.')
            return redirect(list_url)
        items = InventoryItem.objects.filter(pk__in=ids)
        if 'confirm' in request.POST:
            count = items.count()
            ids_str = list(items.values_list('pk', flat=True))
            with transaction.atomic():
                items.delete()
            AuditLog.objects.create(
                user=request.user, action='bulk_delete', model_name='InventoryItem',
                object_repr=f'{count} inventory items', details={'ids': ids_str, 'count': count},
            )
            messages.success(request, f'{count} inventory item{"s" if count != 1 else ""} deleted.')
            return redirect(list_url + ('?' + next_qs if next_qs else ''))
        return render(request, 'inventory/bulk_delete.html', {
            'items': items,
            'item_ids': ids,
            'next_qs': next_qs,
        })
    return redirect('inventory:inventory_list')


@login_required
@finance_admin_required('inventory:inventory_list')
def inventory_bulk_edit(request):
    """Edit shared fields on multiple inventory items selected via checkboxes."""
    list_url = 'inventory:inventory_list'
    if request.method == 'POST':
        ids = request.POST.getlist('item_ids')
        next_qs = request.POST.get('next_qs', '')
        if not ids:
            messages.error(request, 'No items selected.')
            return redirect(list_url)
        items = InventoryItem.objects.filter(pk__in=ids)
        if 'apply' in request.POST:
            form = InventoryItemBulkEditForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                changes = {}
                if data.get('location'):
                    changes['location'] = data['location']
                if data.get('reorder_level') is not None:
                    changes['reorder_level'] = data['reorder_level']
                if changes:
                    count = 0
                    with transaction.atomic():
                        for item in items:
                            for field, value in changes.items():
                                setattr(item, field, value)
                            item.updated_by = request.user
                            item.save()
                            count += 1
                    AuditLog.objects.create(
                        user=request.user, action='bulk_edit', model_name='InventoryItem',
                        object_repr=f'{count} inventory items updated',
                        details={'ids': list(items.values_list('pk', flat=True)),
                                 'fields': list(changes), 'count': count},
                    )
                    messages.success(request, f'{count} inventory item{"s" if count != 1 else ""} updated.')
                else:
                    messages.info(request, 'No changes selected — nothing was updated.')
                return redirect(list_url + ('?' + next_qs if next_qs else ''))
        else:
            form = InventoryItemBulkEditForm()
        return render(request, 'inventory/bulk_edit.html', {
            'items': items,
            'item_ids': ids,
            'form': form,
            'next_qs': next_qs,
        })
    return redirect(list_url)

@login_required
def reorder_list(request):
    items = InventoryItem.objects.select_related('category', 'location').annotate(
        balance=ExpressionWrapper(F('opening_stock') + F('received_qty') - F('issued_qty'), output_field=IntegerField())
    ).filter(balance__lte=F('reorder_level'), balance__gt=0)
    return render(request, 'reports/reorder_list.html', {'items': items})
