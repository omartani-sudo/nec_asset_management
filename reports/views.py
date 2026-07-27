# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, ExpressionWrapper, IntegerField
from django.http import HttpResponse
from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem
from lists.models import Status
from datetime import date
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

def generate_chart_image(labels, values, title, kind='bar'):
    fig, ax = plt.subplots(figsize=(10, 5))
    if kind == 'bar':
        ax.bar([str(l) for l in labels], [float(v) for v in values])
    else:
        ax.plot([str(l) for l in labels], [float(v) for v in values], marker='o')
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode('utf-8')

def export_to_excel(df, filename):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return response

@login_required
def reports_home(request):
    return render(request, 'reports/home.html')

@login_required
def asset_status_report(request):
    qs = FixedAsset.objects.values('status__name').annotate(count=Count('id'))
    labels = [r['status__name'] for r in qs]
    values = [r['count'] for r in qs]
    chart = generate_chart_image(labels, values, 'Asset Status Distribution', kind='bar')
    return render(request, 'reports/asset_status.html', {'data': qs, 'chart': chart, 'export_url': 'reports:export_asset_status'})

@login_required
def fixed_assets_by_category(request):
    data = FixedAsset.objects.values('category__name').annotate(count=Count('id'), total_cost=Sum('purchase_cost'), total_nbv=Sum('purchase_cost'))
    labels = [r['category__name'] for r in data]
    values = [float(r['total_cost'] or 0) for r in data]
    chart = generate_chart_image(labels, values, 'Fixed Assets by Category (Cost)', kind='bar')
    return render(request, 'reports/fixed_assets_summary.html', {'data': data, 'chart': chart, 'title': 'Fixed Assets by Category', 'export_url': 'reports:export_fixed_assets_category'})

@login_required
def fixed_assets_by_department(request):
    data = FixedAsset.objects.values('department__name').annotate(count=Count('id'), total_cost=Sum('purchase_cost'), total_nbv=Sum('purchase_cost'))
    labels = [r['department__name'] for r in data]
    values = [float(r['total_cost'] or 0) for r in data]
    chart = generate_chart_image(labels, values, 'Fixed Assets by Department (Cost)', kind='bar')
    return render(request, 'reports/fixed_assets_summary.html', {'data': data, 'chart': chart, 'title': 'Fixed Assets by Department', 'export_url': 'reports:export_fixed_assets_department'})

@login_required
def inventory_summary(request):
    data = InventoryItem.objects.values('category__name').annotate(count=Count('id'), total_value=Sum('unit_cost'))
    return render(request, 'reports/inventory_summary.html', {'data': data, 'title': 'Inventory Summary', 'export_url': 'reports:export_inventory_summary'})

@login_required
def reorder_report(request):
    items = InventoryItem.objects.select_related('category', 'location').annotate(
        balance=ExpressionWrapper(F('opening_stock') + F('received_qty') - F('issued_qty'), output_field=IntegerField())
    ).filter(balance__lte=F('reorder_level'))
    return render(request, 'reports/reorder_list.html', {'items': items})

@login_required
def export_fixed_assets_category(request):
    data = FixedAsset.objects.values('category__name').annotate(count=Count('id'), total_cost=Sum('purchase_cost'), total_nbv=Sum('purchase_cost'))
    df = pd.DataFrame(list(data))
    df.columns = ['Category', 'Count', 'Total Purchase Cost', 'Total NBV']
    return export_to_excel(df, 'fixed_assets_by_category.xlsx')

@login_required
def export_fixed_assets_department(request):
    data = FixedAsset.objects.values('department__name').annotate(count=Count('id'), total_cost=Sum('purchase_cost'), total_nbv=Sum('purchase_cost'))
    df = pd.DataFrame(list(data))
    df.columns = ['Department', 'Count', 'Total Purchase Cost', 'Total NBV']
    return export_to_excel(df, 'fixed_assets_by_department.xlsx')

@login_required
def export_asset_status(request):
    data = FixedAsset.objects.values('status__name').annotate(count=Count('id'))
    df = pd.DataFrame(list(data))
    df.columns = ['Status', 'Count']
    return export_to_excel(df, 'asset_status.xlsx')

@login_required
def export_inventory_summary(request):
    data = InventoryItem.objects.values('category__name').annotate(count=Count('id'), total_value=Sum('unit_cost'))
    df = pd.DataFrame(list(data))
    df.columns = ['Category', 'Count', 'Total Value']
    return export_to_excel(df, 'inventory_summary.xlsx')

@login_required
def export_reorder_list(request):
    items = InventoryItem.objects.select_related('category', 'location').annotate(
        balance=ExpressionWrapper(F('opening_stock') + F('received_qty') - F('issued_qty'), output_field=IntegerField())
    ).filter(balance__lte=F('reorder_level'))
    data = [{'Item Code': i.item_code, 'Description': i.description, 'Category': i.category.name, 'Balance Qty': i.balance, 'Reorder Level': i.reorder_level} for i in items]
    df = pd.DataFrame(data)
    return export_to_excel(df, 'reorder_list.xlsx')
