# -*- coding: utf-8 -*-
"""Tests for the audit trail (signals, middleware attribution, page access)."""
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status
from fixed_assets.models import FixedAsset
from core.models import AuditLog

User = get_user_model()


class AuditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.finance = User.objects.create_user(username='finance', password='pass12345', role='finance', email='fin@nec.gov')
        self.viewer = User.objects.create_user(username='viewer', password='pass12345', role='viewer')

        self.category = Category.objects.create(name='Cat', code='CAT')
        self.department = Department.objects.create(name='Dept')
        self.location = Location.objects.create(name='Loc')
        self.status = Status.objects.create(name='In Use')

    def _make_asset(self, name='Audited asset'):
        return FixedAsset.objects.create(
            asset_name=name, category=self.category, department=self.department,
            location=self.location, status=self.status,
            purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000'), useful_life=5,
        )

    def test_create_records_audit_entry(self):
        self.client.force_login(self.finance)
        self.client.post(reverse('fixed_assets:fixed_asset_create'), {
            'asset_name': 'New audited', 'category': self.category.pk,
            'department': self.department.pk, 'location': self.location.pk,
            'status': self.status.pk, 'purchase_date': '2024-01-01',
            'purchase_cost': '1000', 'useful_life': 5, 'salvage_value': '0',
            'depreciation_method': 'SL', 'condition': 'new', 'disposal_date': '',
            'serial_number': '', 'supplier': '', 'notes': '',
        })
        entry = AuditLog.objects.filter(action='create', model_name='FixedAsset').first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.user, self.finance)

    def test_update_and_delete_record_entries(self):
        asset = self._make_asset()
        self.client.force_login(self.admin)
        self.client.post(reverse('fixed_assets:fixed_asset_update', args=[asset.pk]), {
            'asset_name': 'Renamed', 'category': self.category.pk,
            'department': self.department.pk, 'location': self.location.pk,
            'status': self.status.pk, 'purchase_date': '2024-01-01',
            'purchase_cost': '1000', 'useful_life': 5, 'salvage_value': '0',
            'depreciation_method': 'SL', 'condition': 'new', 'disposal_date': '',
            'serial_number': asset.serial_number, 'supplier': '', 'notes': '',
        })
        self.assertTrue(AuditLog.objects.filter(action='update', model_name='FixedAsset', object_id=str(asset.pk)).exists())

        self.client.post(reverse('fixed_assets:fixed_asset_delete', args=[asset.pk]))
        self.assertTrue(AuditLog.objects.filter(action='delete', model_name='FixedAsset', object_id=str(asset.pk)).exists())

    def test_bulk_delete_records_summary_entry(self):
        a1, a2 = self._make_asset('One'), self._make_asset('Two')
        self.client.force_login(self.admin)
        self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_delete'),
            {'asset_ids': [str(a1.pk), str(a2.pk)], 'confirm': '1'},
        )
        summary = AuditLog.objects.filter(action='bulk_delete', model_name='FixedAsset').first()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.details['count'], 2)

    def test_audit_page_admin_and_finance_only(self):
        self.client.force_login(self.viewer)
        resp = self.client.get(reverse('core:audit_log'))
        self.assertRedirects(resp, reverse('dashboard:dashboard'))
        self.client.force_login(self.finance)
        resp = self.client.get(reverse('core:audit_log'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Audit Log')

    def test_audit_page_filters(self):
        self._make_asset('Filterable')
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('core:audit_log'), {'action': 'create', 'model_name': 'FixedAsset'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(all(e.action == 'create' for e in resp.context['page_obj']))

    def test_no_recursion_writing_auditlog(self):
        # AuditLog saves must not create further AuditLog rows
        before = AuditLog.objects.count()
        AuditLog.objects.create(action='create', model_name='FixedAsset', object_repr='x')
        self.assertEqual(AuditLog.objects.count(), before + 1)
