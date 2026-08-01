# -*- coding: utf-8 -*-
"""
Shared Excel import logic for NEC Asset Registry.
Used by both the management command and the web upload view.
"""
import pandas as pd
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from lists.models import Category, Department, Location, Status, Unit
from fixed_assets.models import FixedAsset

User = get_user_model()


def safe_str(val):
    """Clean NaN/None to empty string."""
    if pd.isna(val) or val is None:
        return ''
    return str(val).strip()


def safe_decimal(val):
    """Convert to Decimal, return None if invalid."""
    if pd.isna(val) or val is None or str(val).strip() == '':
        return None
    try:
        return Decimal(str(val).replace(',', '').replace('$', '').strip())
    except (InvalidOperation, ValueError):
        return None


def safe_date(val):
    """Convert to date, return None if invalid."""
    if pd.isna(val) or val is None or str(val).strip() == '':
        return None
    try:
        if isinstance(val, datetime):
            return val.date()
        return datetime.strptime(str(val).strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        try:
            return pd.to_datetime(val).date()
        except Exception:
            return None


def safe_int(val):
    """Convert to int, return None if invalid."""
    if pd.isna(val) or val is None or str(val).strip() == '':
        return None
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return None


def import_lists(file_source, stdout=None):
    """Extract and import reference lists from the Lists sheet.

    Args:
        file_source: File path string OR a file-like object (BytesIO/UploadedFile).
        stdout: Optional output stream for progress messages.

    Returns:
        dict with keys: categories, departments, locations, statuses, units
    """
    def log(msg, style=None):
        if stdout:
            if style:
                stdout.write(style(msg))
            else:
                stdout.write(msg)

    log('\n--- Importing Reference Lists ---')

    df = pd.read_excel(file_source, sheet_name='Lists', engine='openpyxl')

    # Column 0: Category names
    categories = df.iloc[:, 0].dropna().drop_duplicates().tolist()
    # Column 8: Category codes
    codes = df.iloc[:, 8].dropna().drop_duplicates().tolist()

    created_cats = {}
    for i, cat_name in enumerate(categories):
        code = codes[i] if i < len(codes) else cat_name[:3].upper()
        obj, created = Category.objects.get_or_create(
            name=safe_str(cat_name),
            defaults={'code': safe_str(code)}
        )
        created_cats[safe_str(cat_name)] = obj
        if created:
            log(f'  Category: {obj.name} ({obj.code})')

    # Column 1: Department names
    departments = df.iloc[:, 1].dropna().drop_duplicates().tolist()
    dept_count = 0
    for dept_name in departments:
        obj, created = Department.objects.get_or_create(name=safe_str(dept_name))
        if created:
            dept_count += 1

    # Column 2: Location names
    locations = df.iloc[:, 2].dropna().drop_duplicates().tolist()
    loc_count = 0
    for loc_name in locations:
        obj, created = Location.objects.get_or_create(name=safe_str(loc_name))
        if created:
            loc_count += 1

    # Column 3: Status names
    statuses = df.iloc[:, 3].dropna().drop_duplicates().tolist()
    status_count = 0
    for status_name in statuses:
        obj, created = Status.objects.get_or_create(name=safe_str(status_name))
        if created:
            status_count += 1

    # Column 6: Inventory categories -> Units
    units = df.iloc[:, 6].dropna().drop_duplicates().tolist()
    unit_count = 0
    for unit_name in units:
        obj, created = Unit.objects.get_or_create(name=safe_str(unit_name))
        if created:
            unit_count += 1

    log(f'  Lists: {len(created_cats)} categories, {dept_count} departments, '
        f'{loc_count} locations, {status_count} statuses, {unit_count} units')

    return {
        'categories': created_cats,
        'departments': dept_count,
        'locations': loc_count,
        'statuses': status_count,
        'units': unit_count,
    }


def import_fixed_assets(file_source, stdout=None):
    """Import fixed assets from the Fixed_Assets sheet.

    Args:
        file_source: File path string OR a file-like object (BytesIO/UploadedFile).
        stdout: Optional output stream for progress messages.

    Returns:
        dict with keys: imported (int), skipped (int), errors (list)
    """
    def log(msg, style=None):
        if stdout:
            if style:
                stdout.write(style(msg))
            else:
                stdout.write(msg)

    log('\n--- Importing Fixed Assets ---')

    df = pd.read_excel(file_source, sheet_name='Fixed_Assets', header=None, engine='openpyxl')

    # Find the header row (row containing "Asset ID")
    header_row = None
    for idx, row in df.iterrows():
        first_cell = str(row.iloc[0]).strip()
        if first_cell == 'Asset ID':
            header_row = idx
            break

    if header_row is None:
        msg = 'Could not find "Asset ID" header row in Fixed_Assets sheet'
        log(msg)
        return {'imported': 0, 'skipped': 0, 'errors': [(None, None, msg)]}

    data_start = header_row + 1
    admin_user = User.objects.filter(is_superuser=True).first()

    imported = 0
    skipped = 0
    errors = []

    for idx in range(data_start, len(df)):
        row = df.iloc[idx]
        asset_name = safe_str(row.iloc[1])

        # Skip empty rows, total rows, and informational rows
        if not asset_name:
            continue
        if asset_name.startswith('WADARTA') or asset_name.startswith('Fiiro'):
            continue

        asset_id = safe_str(row.iloc[0])
        if not asset_id:
            skipped += 1
            continue

        # Check if already exists
        if FixedAsset.objects.filter(asset_id=asset_id).exists():
            log(f'  SKIP (exists): {asset_id} - {asset_name}')
            skipped += 1
            continue

        # Resolve foreign keys
        cat_name = safe_str(row.iloc[2])
        dept_name = safe_str(row.iloc[3])
        loc_name = safe_str(row.iloc[4])
        status_name = safe_str(row.iloc[15])

        category = Category.objects.filter(name=cat_name).first()
        department = Department.objects.filter(name=dept_name).first() or Department.objects.first()
        location = Location.objects.filter(name=loc_name).first() or Location.objects.first()
        status = Status.objects.filter(name=status_name).first() or Status.objects.first()

        # Parse fields
        purchase_cost = safe_decimal(row.iloc[8]) or Decimal('0')
        useful_life = safe_int(row.iloc[9]) or 5
        salvage_value = safe_decimal(row.iloc[10]) or Decimal('0')
        dep_method_raw = safe_str(row.iloc[11])

        # Map depreciation method
        dep_method_map = {
            'Straight Line': 'SL', 'SL': 'SL', 'SLN': 'SL',
            'Reducing Balance': 'RB', 'RB': 'RB', 'DDB': 'RB',
        }
        dep_method = dep_method_map.get(dep_method_raw, 'SL')

        # Map condition
        condition_raw = safe_str(row.iloc[17]).lower()
        condition_map = {
            'cusub (new)': 'new', 'new': 'new',
            'wanaagsan (good)': 'good', 'good': 'good',
            'dhexdhexaad (fair)': 'fair', 'fair': 'fair',
            'xun (poor)': 'poor', 'poor': 'poor',
            'broken': 'broken',
        }
        condition = condition_map.get(condition_raw, 'new')

        purchase_date = safe_date(row.iloc[7])
        if purchase_date is None:
            purchase_date = datetime.now().date()

        disposal_date = safe_date(row.iloc[18])

        assigned_to_raw = safe_str(row.iloc[16])
        assigned_to = admin_user
        if assigned_to_raw and assigned_to_raw not in ('hjh', 'NaN', 'nan', ''):
            found_user = User.objects.filter(username__iexact=assigned_to_raw).first()
            if found_user:
                assigned_to = found_user

        # Clean garbage values
        serial = safe_str(row.iloc[5])
        if serial.lower() in ('hjh', 'nan', ''):
            serial = ''
        supplier = safe_str(row.iloc[6])
        if supplier.lower() in ('hjh', 'nan', ''):
            supplier = ''

        try:
            with transaction.atomic():
                asset = FixedAsset.objects.create(
                    asset_id=asset_id,
                    asset_name=asset_name,
                    category=category,
                    department=department,
                    location=location,
                    serial_number=serial,
                    supplier=supplier,
                    purchase_date=purchase_date or datetime.now().date(),
                    purchase_cost=purchase_cost or Decimal('0'),
                    useful_life=useful_life or 5,
                    salvage_value=salvage_value,
                    depreciation_method=dep_method,
                    status=status,
                    assigned_to=assigned_to,
                    condition=condition,
                    disposal_date=disposal_date,
                    notes=safe_str(row.iloc[19]),
                    created_by=admin_user,
                    updated_by=admin_user,
                )
            log(f'  IMPORTED: {asset.asset_id} - {asset.asset_name} | '
                f'Cost: ${asset.purchase_cost} | {asset.depreciation_method} | {asset.useful_life}yr')
            imported += 1
        except IntegrityError:
            # Duplicate asset_id — another user/concurrent upload already imported this
            log(f'  SKIP (duplicate): {asset_id} - {asset_name}')
            skipped += 1
        except Exception as e:
            error_msg = str(e)
            log(f'  FAILED: {asset_id} - {asset_name}: {error_msg}')
            errors.append((asset_id, asset_name, error_msg))
            skipped += 1

    log(f'\nFixed Assets: {imported} imported, {skipped} skipped')

    return {
        'imported': imported,
        'skipped': skipped,
        'errors': errors,
    }
