# -*- coding: utf-8 -*-
"""Tests for filtered Excel exports of fixed and current asset lists."""
import io
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status
from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset

User = get_user_model()


class ExportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.client.force_login(self.admin)

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.dept = Department.objects.create(name='Dept')
        self.loc = Location.objects.create(name='Loc')
        self.status = Status.objects.create(name='In Use')

        for i in range(3):
            FixedAsset.objects.create(
                asset_name=f'Fixed {i}', category=self.cat, department=self.dept,
                location=self.loc, status=self.status,
                purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000'), useful_life=5,
            )
            CurrentAsset.objects.create(
                description=f'Current {i}', category=self.cat, department=self.dept,
                location=self.loc, status=self.status, value=Decimal('100'),
            )

    def _read_xlsx_rows(self, response):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        return [cell.value for cell in ws[1]], list(ws.iter_rows(min_row=2, values_only=True))

    def test_fixed_export_content_type_and_rows(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_export'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheetml', resp['Content-Type'])
        headers, rows = self._read_xlsx_rows(resp)
        self.assertIn('Asset ID', headers)
        self.assertEqual(len(rows), 3)

    def test_fixed_export_respects_filters(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_export'), {'q': 'Fixed 1'})
        _, rows = self._read_xlsx_rows(resp)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'Fixed 1')

    def test_current_export(self):
        resp = self.client.get(reverse('current_assets:current_asset_export'))
        self.assertEqual(resp.status_code, 200)
        headers, rows = self._read_xlsx_rows(resp)
        self.assertIn('Description', headers)
        self.assertEqual(len(rows), 3)
