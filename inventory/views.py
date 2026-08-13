# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, IntegerField
from .models import InventoryItem
from lists.models import Category, Location, Status, Unit
from .forms import InventoryItemForm
from core.decorators import admin_required

@login_required
def inventory_list(request):
    items = InventoryItem.objects.select_related('category', 'unit', 'location').all()
    return render(request, 'inventory/list.html', {'items': items})

@login_required
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
        if not ids:
            messages.error(request, 'No items selected.')
            return redirect('inventory:inventory_list')
        items = InventoryItem.objects.filter(pk__in=ids)
        if 'confirm' in request.POST:
            count = items.count()
            with transaction.atomic():
                items.delete()
            messages.success(request, f'{count} inventory item{"s" if count != 1 else ""} deleted.')
            return redirect('inventory:inventory_list')
        return render(request, 'inventory/bulk_delete.html', {
            'items': items,
            'item_ids': ids,
        })
    return redirect('inventory:inventory_list')

@login_required
def reorder_list(request):
    items = InventoryItem.objects.select_related('category', 'location').annotate(
        balance=ExpressionWrapper(F('opening_stock') + F('received_qty') - F('issued_qty'), output_field=IntegerField())
    ).filter(balance__lte=F('reorder_level'), balance__gt=0)
    return render(request, 'reports/reorder_list.html', {'items': items})
