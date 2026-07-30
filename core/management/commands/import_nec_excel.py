# -*- coding: utf-8 -*-
"""
Management command to import NEC Asset Register Excel file.
Usage: python manage.py import_nec_excel /path/to/file.xlsx
"""
import pandas as pd
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lists.models import Category, Department, Location, Status, Unit
from fixed_assets.models import FixedAsset

User = get_user_model()


class Command(BaseCommand):
    help = 'Import NEC Asset Registration Excel into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def safe_str(self, val):
        """Clean NaN/None to empty string."""
        if pd.isna(val) or val is None:
            return ''
        return str(val).strip()

    def safe_decimal(self, val):
        """Convert to Decimal, return None if invalid."""
        if pd.isna(val) or val is None or str(val).strip() == '':
            return None
        try:
            return Decimal(str(val).replace(',', '').replace('$', '').strip())
        except (InvalidOperation, ValueError):
            return None

    def safe_date(self, val):
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

    def safe_int(self, val):
        """Convert to int, return None if invalid."""
        if pd.isna(val) or val is None or str(val).strip() == '':
            return None
        try:
            return int(float(str(val).strip()))
        except (ValueError, TypeError):
            return None

    def import_lists(self, file_path):
        """Extract and import reference lists from the Lists sheet."""
        self.stdout.write('\n--- Importing Reference Lists ---')

        df = pd.read_excel(file_path, sheet_name='Lists')

        # Column 0: Category names
        categories = df.iloc[:, 0].dropna().drop_duplicates().tolist()
        # Column 8: Category codes (e.g., BLD, VEH, ITE, OFF, MCH, FUR, OTH, ELM)
        codes = df.iloc[:, 8].dropna().drop_duplicates().tolist()

        created_cats = {}
        for i, cat_name in enumerate(categories):
            code = codes[i] if i < len(codes) else cat_name[:3].upper()
            obj, created = Category.objects.get_or_create(
                name=self.safe_str(cat_name),
                defaults={'code': self.safe_str(code)}
            )
            created_cats[self.safe_str(cat_name)] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Category: {obj.name} ({obj.code})'))
            else:
                self.stdout.write(f'  Category (exists): {obj.name}')

        # Column 1: Department names
        departments = df.iloc[:, 1].dropna().drop_duplicates().tolist()
        for dept_name in departments:
            obj, created = Department.objects.get_or_create(name=self.safe_str(dept_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Department: {obj.name}'))

        # Column 2: Location names
        locations = df.iloc[:, 2].dropna().drop_duplicates().tolist()
        for loc_name in locations:
            obj, created = Location.objects.get_or_create(name=self.safe_str(loc_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Location: {obj.name}'))

        # Column 3: Status names
        statuses = df.iloc[:, 3].dropna().drop_duplicates().tolist()
        for status_name in statuses:
            obj, created = Status.objects.get_or_create(name=self.safe_str(status_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Status: {obj.name}'))

        # Column 6: Inventory categories → Units
        units = df.iloc[:, 6].dropna().drop_duplicates().tolist()
        for unit_name in units:
            obj, created = Unit.objects.get_or_create(name=self.safe_str(unit_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Unit: {obj.name}'))

        return created_cats

    def import_fixed_assets(self, file_path):
        """Import fixed assets from the Fixed_Assets sheet."""
        self.stdout.write('\n--- Importing Fixed Assets ---')

        df = pd.read_excel(file_path, sheet_name='Fixed_Assets', header=None)

        # Find the header row (row containing "Asset ID")
        header_row = None
        for idx, row in df.iterrows():
            first_cell = str(row.iloc[0]).strip()
            if first_cell == 'Asset ID':
                header_row = idx
                break

        if header_row is None:
            self.stdout.write(self.style.ERROR('Could not find "Asset ID" header row'))
            return

        # Read data starting from header_row
        # Columns: Asset ID, Asset Name, Category, Department, Location,
        #           Serial Number, Supplier, Purchase Date, Purchase Cost,
        #           Useful Life, Salvage Value, Depreciation Method,
        #           Annual Depreciation, Accumulated Depreciation, Net Book Value,
        #           Status, Assigned To, Condition, Disposal Date, Notes
        data_start = header_row + 1
        admin_user = User.objects.filter(is_superuser=True).first()

        imported = 0
        skipped = 0

        for idx in range(data_start, len(df)):
            row = df.iloc[idx]
            asset_name = self.safe_str(row.iloc[1])

            # Skip empty rows, total rows, and informational rows
            if not asset_name:
                continue
            if asset_name.startswith('WADARTA') or asset_name.startswith('Fiiro'):
                continue

            asset_id = self.safe_str(row.iloc[0])
            if not asset_id:
                skipped += 1
                continue

            # Check if already exists
            if FixedAsset.objects.filter(asset_id=asset_id).exists():
                self.stdout.write(f'  SKIP (exists): {asset_id} - {asset_name}')
                skipped += 1
                continue

            # Resolve foreign keys with defaults for missing data
            cat_name = self.safe_str(row.iloc[2])
            dept_name = self.safe_str(row.iloc[3])
            loc_name = self.safe_str(row.iloc[4])
            status_name = self.safe_str(row.iloc[15])

            category = Category.objects.filter(name=cat_name).first()
            department = Department.objects.filter(name=dept_name).first() or Department.objects.first()
            location = Location.objects.filter(name=loc_name).first() or Location.objects.first()
            status = Status.objects.filter(name=status_name).first() or Status.objects.first()

            # Parse fields — use defaults when Excel data is missing
            purchase_cost = self.safe_decimal(row.iloc[8]) or Decimal('0')
            useful_life = self.safe_int(row.iloc[9]) or 5
            salvage_value = self.safe_decimal(row.iloc[10]) or Decimal('0')
            dep_method_raw = self.safe_str(row.iloc[11])

            # Map depreciation method
            dep_method_map = {
                'Straight Line': 'SL', 'SL': 'SL', 'SLN': 'SL',
                'Reducing Balance': 'RB', 'RB': 'RB', 'DDB': 'RB',
            }
            dep_method = dep_method_map.get(dep_method_raw, 'SL')

            # Map condition
            condition_raw = self.safe_str(row.iloc[17]).lower()
            condition_map = {
                'cusub (new)': 'new', 'new': 'new',
                'wanaagsan (good)': 'good', 'good': 'good',
                'dhexdhexaad (fair)': 'fair', 'fair': 'fair',
                'xun (poor)': 'poor', 'poor': 'poor',
                'broken': 'broken',
            }
            condition = condition_map.get(condition_raw, 'new')

            purchase_date = self.safe_date(row.iloc[7])
            if purchase_date is None:
                purchase_date = datetime.now().date()

            disposal_date = self.safe_date(row.iloc[18])

            assigned_to_raw = self.safe_str(row.iloc[16])
            assigned_to = admin_user
            if assigned_to_raw and assigned_to_raw not in ('hjh', 'NaN', 'nan', ''):
                found_user = User.objects.filter(username__iexact=assigned_to_raw).first()
                if found_user:
                    assigned_to = found_user

            # Clean garbage values from serial/supplier
            serial = self.safe_str(row.iloc[5])
            if serial.lower() in ('hjh', 'nan', ''):
                serial = ''
            supplier = self.safe_str(row.iloc[6])
            if supplier.lower() in ('hjh', 'nan', ''):
                supplier = ''

            try:
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
                    notes=self.safe_str(row.iloc[19]),
                    created_by=admin_user,
                    updated_by=admin_user,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'  IMPORTED: {asset.asset_id} - {asset.asset_name} | '
                    f'Cost: ${asset.purchase_cost} | {asset.depreciation_method} | {asset.useful_life}yr'
                ))
                imported += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  FAILED: {asset_id} - {asset_name}: {e}'
                ))
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nFixed Assets: {imported} imported, {skipped} skipped'
        ))

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.stdout.write(self.style.SUCCESS(f'Importing from: {file_path}'))

        # Import reference lists first
        self.import_lists(file_path)

        # Import fixed assets
        self.import_fixed_assets(file_path)

        self.stdout.write(self.style.SUCCESS('\n=== Import Complete ==='))
