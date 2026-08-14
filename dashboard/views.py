# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField, Sum, Count
from fixed_assets.models import FixedAsset, DepreciationSchedule
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem
from lists.models import Department


def depreciation_chart_data(department=None):
    """Yearly depreciation totals for the Chart.js trend chart."""
    schedules = DepreciationSchedule.objects.select_related('asset')
    if department:
        schedules = schedules.filter(asset__department=department)
    year_totals = {}
    for s in schedules.order_by('year_number'):
        year_totals[s.year_number] = year_totals.get(s.year_number, 0) + float(s.annual_depreciation)
    years = sorted(year_totals)
    return {
        'years': years,
        'values': [round(year_totals[y], 2) for y in years],
    }


@login_required
def dashboard(request):
    # Optional department filter (?department=<id>)
    selected_department = None
    dept_param = request.GET.get('department', '')
    if dept_param and dept_param.isdigit():
        selected_department = get_object_or_404(Department, pk=int(dept_param))

    assets = FixedAsset.objects.all()
    current_assets = CurrentAsset.objects.all()
    if selected_department:
        assets = assets.filter(department=selected_department)
        current_assets = current_assets.filter(department=selected_department)

    total_fixed = assets.count()
    total_purchase_cost = sum(float(a.purchase_cost) for a in assets)
    total_accumulated_depr = sum(float(a.accumulated_depreciation()) for a in assets)
    total_net_book_value = sum(float(a.net_book_value()) for a in assets)

    total_current = sum(float(c.value) for c in current_assets)
    total_inventory = sum(float(i.total_value) for i in InventoryItem.objects.all())

    inventory_annotated = InventoryItem.objects.annotate(
        balance=ExpressionWrapper(
            F('opening_stock') + F('received_qty') - F('issued_qty'),
            output_field=IntegerField()
        )
    )
    reorder_needed = inventory_annotated.filter(
        balance__lte=F('reorder_level'), balance__gt=0
    ).count()
    out_of_stock = inventory_annotated.filter(balance=0).count()
    disposed_count = assets.filter(
        status__name__icontains='Disposed'
    ).count()

    category_data = (
        assets.values('category__name')
        .annotate(count=Count('id'), total_cost=Sum('purchase_cost'))
        .order_by('-count')
    )

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
        'chart_data': depreciation_chart_data(department=selected_department),
        'category_data': list(category_data),
        'departments': Department.objects.filter(is_active=True),
        'selected_department': selected_department,
    }
    return render(request, 'dashboard/dashboard.html', context)
