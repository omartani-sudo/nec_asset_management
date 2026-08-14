# -*- coding: utf-8 -*-
import io
import base64
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField, Sum, Count
from fixed_assets.models import FixedAsset, DepreciationSchedule
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem
from lists.models import Department
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.dates import DateFormatter
import numpy as np


def generate_depreciation_chart_base64(department=None):
    """Generate a base64-encoded PNG of the depreciation trend chart using
    actual depreciation schedule data for the most accurate projection."""
    schedules = DepreciationSchedule.objects.select_related('asset')
    if department:
        schedules = schedules.filter(asset__department=department)
    schedules = schedules.order_by('asset', 'year_number')

    if not schedules.exists():
        return ''

    # Aggregate annual depreciation across all assets
    year_totals = {}
    for s in schedules:
        year_totals[s.year_number] = year_totals.get(s.year_number, 0) + float(s.annual_depreciation)

    years = sorted(year_totals.keys())
    annual_depreciation = [year_totals[y] for y in years]

    # Create the chart with NEC branding
    fig, ax = plt.subplots(figsize=(10, 4.5))

    # NEC brand colors
    nec_blue = '#0d6efd'
    nec_dark = '#1a3a5c'
    grid_color = '#e0e0e0'

    ax.fill_between(years, annual_depreciation, alpha=0.15, color=nec_blue)
    ax.plot(years, annual_depreciation, color=nec_blue, linewidth=2.5, marker='o',
            markersize=6, markerfacecolor='white', markeredgewidth=2, markeredgecolor=nec_blue)

    # Formatting
    ax.set_xlabel('Year', fontsize=11, color=nec_dark, fontweight='600')
    ax.set_ylabel('Annual Depreciation ($)', fontsize=11, color=nec_dark, fontweight='600')
    ax.set_title('Depreciation Trend (Annual)', fontsize=14, fontweight='bold', color=nec_dark, pad=15)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.grid(True, linestyle='--', alpha=0.4, color=grid_color)
    ax.set_axisbelow(True)

    # Set x-axis ticks to match actual years
    if len(years) <= 10:
        ax.set_xticks(years)

    # Add value labels on data points
    for x, y in zip(years, annual_depreciation):
        if y > 0:
            ax.annotate(f'${y:,.0f}', (x, y), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=8, color=nec_dark, fontweight='600')

    fig.tight_layout(pad=1.5)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


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

    # Category breakdown for pie chart
    category_data = (
        assets.values('category__name')
        .annotate(count=Count('id'), total_cost=Sum('purchase_cost'))
        .order_by('-count')
    )

    # Generate depreciation trend chart
    chart_base64 = generate_depreciation_chart_base64(department=selected_department)

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
        'chart_base64': chart_base64,
        'category_data': list(category_data),
        'departments': Department.objects.filter(is_active=True),
        'selected_department': selected_department,
    }
    return render(request, 'dashboard/dashboard.html', context)
