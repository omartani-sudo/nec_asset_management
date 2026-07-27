# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField
from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem
from datetime import date

def generate_depreciation_trend(assets):
    years = list(range(1, 11))
    annual_totals = []
    for year in years:
        total = 0
        for asset in assets:
            if asset.depreciation_method == 'SL':
                total += float(asset.annual_depreciation())
            else:
                nbv = float(asset.purchase_cost)
                for y in range(year):
                    dep = (nbv - float(asset.salvage_value)) * (2 / asset.useful_life)
                    if nbv - dep <= float(asset.salvage_value):
                        dep = nbv - float(asset.salvage_value)
                    nbv -= dep
                    if nbv <= float(asset.salvage_value):
                        break
                total += dep
        annual_totals.append(round(total, 2))
    return years, annual_totals

@login_required
def dashboard(request):
    total_fixed = FixedAsset.objects.count()
    total_purchase_cost = sum(float(a.purchase_cost) for a in FixedAsset.objects.all())
    total_accumulated_depr = sum(float(a.accumulated_depreciation()) for a in FixedAsset.objects.all())
    total_net_book_value = sum(float(a.net_book_value()) for a in FixedAsset.objects.all())
    total_current = sum(float(c.value) for c in CurrentAsset.objects.all())
    total_inventory = sum(float(i.total_value) for i in InventoryItem.objects.all())
    inventory_annotated = InventoryItem.objects.annotate(
        balance=ExpressionWrapper(F('opening_stock') + F('received_qty') - F('issued_qty'), output_field=IntegerField())
    )
    reorder_needed = inventory_annotated.filter(balance__lte=F('reorder_level'), balance__gt=0).count()
    out_of_stock = inventory_annotated.filter(balance=0).count()
    disposed_count = FixedAsset.objects.filter(status__name__iexact='Disposed').count()

    assets = FixedAsset.objects.all()
    years, trend_data = generate_depreciation_trend(assets)

    context = {
        'total_fixed': total_fixed,
        'total_purchase_cost': total_purchase_cost,
        'total_accumulated_depr': total_accumulated_depr,
        'total_net_book_value': total_net_book_value,
        'total_current': total_current,
        'total_inventory': total_inventory,
        'reorder_needed': reorder_needed,
        'out_of_stock': out_of_stock,
        'disposed_count': disposed_count,
        'depreciation_years': years,
        'depreciation_trend': trend_data,
    }
    return render(request, 'dashboard/dashboard.html', context)
