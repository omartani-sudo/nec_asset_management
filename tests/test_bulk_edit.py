# -*- coding: utf-8 -*-
"""Tests for bulk edit (status/location/department changes + role gating)."""
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status, Unit
from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem
from core.models import AuditLog

User = get_user_model()


class BulkEditBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.finance = User.objects.create_user(username='finance', password='pass12345', role='finance')
        self.viewer = User.objects.create_user(username='viewer', password='pass12345', role='viewer')

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.dept = Department.objects.create(name='Dept')
        self.dept2 = Department.objects.create(name='Dept2')
        self.loc = Location.objects.create(name='Loc')
        self.loc2 = Location.objects.create(name='Loc2')
        self.status = Status.objects.create(name='In Use')
        self.status2 = Status.objects.create(name='Damaged')
        self.unit = Unit.objects.create(name='Piece')


class FixedAssetBulkEditTests(BulkEditBase):
    def setUp(self):
        super().setUp()
        self.assets = [
            FixedAsset.objects.create(
                asset_name=f'Asset {i}', category=self.cat, department=self.dept,
                location=self.loc, status=self.status,
                purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000'), useful_life=5,
            ) for i in range(3)
        ]

    def test_finance_bulk_edits_location_and_status(self):
        self.client.force_login(self.finance)
        ids = [str(a.pk) for a in self.assets[:2]]
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_edit'),
            {'asset_ids': ids, 'apply': '1',
             'status': self.status2.pk, 'location': self.loc2.pk,
             'department': '', 'condition': '', 'assigned_to': ''},
        )
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        for a in self.assets[:2]:
            a.refresh_from_db()
            self.assertEqual(a.status_id, self.status2.pk)
            self.assertEqual(a.location_id, self.loc2.pk)
        self.assets[2].refresh_from_db()
        self.assertEqual(self.assets[2].status_id, self.status.pk)

    def test_viewer_blocked_from_bulk_edit(self):
        self.client.force_login(self.viewer)
        ids = [str(a.pk) for a in self.assets]
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_edit'),
            {'asset_ids': ids, 'apply': '1', 'status': self.status2.pk},
        )
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertTrue(FixedAsset.objects.filter(status=self.status).count() == 3)

    def test_dispose_checkbox_sets_disposal_date(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_edit'),
            {'asset_ids': [str(self.assets[0].pk)], 'apply': '1',
             'status': '', 'department': '', 'location': '', 'condition': '',
             'assigned_to': '', 'dispose': 'on'},
        )
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assets[0].refresh_from_db()
        self.assertEqual(self.assets[0].status.name, 'Disposed')
        self.assertEqual(self.assets[0].disposal_date, date.today())

    def test_empty_form_is_noop(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_edit'),
            {'asset_ids': [str(self.assets[0].pk)], 'apply': '1',
             'status': '', 'department': '', 'location': '', 'condition': '', 'assigned_to': ''},
        )
        self.assets[0].refresh_from_db()
        self.assertEqual(self.assets[0].status_id, self.status.pk)

    def test_bulk_edit_audit_entry(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_edit'),
            {'asset_ids': [str(self.assets[0].pk)], 'apply': '1', 'location': self.loc2.pk},
        )
        self.assertTrue(AuditLog.objects.filter(action='bulk_edit', model_name='FixedAsset').exists())

    def test_user_role_blocked_from_single_edit(self):
        user_role = User.objects.create_user(username='plain', password='pass12345', role='user')
        self.client.force_login(user_role)
        resp = self.client.get(reverse('fixed_assets:fixed_asset_update', args=[self.assets[0].pk]))
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        resp = self.client.get(reverse('fixed_assets:fixed_asset_create'))
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))


class CurrentAssetBulkEditTests(BulkEditBase):
    def setUp(self):
        super().setUp()
        self.assets = [
            CurrentAsset.objects.create(
                description=f'Cash {i}', category=self.cat, department=self.dept,
                location=self.loc, status=self.status, value=Decimal('100'),
            ) for i in range(2)
        ]

    def test_bulk_edit_department(self):
        self.client.force_login(self.finance)
        self.client.post(
            reverse('current_assets:current_asset_bulk_edit'),
            {'asset_ids': [str(a.pk) for a in self.assets], 'apply': '1',
             'department': self.dept2.pk, 'status': '', 'location': ''},
        )
        for a in self.assets:
            a.refresh_from_db()
            self.assertEqual(a.department_id, self.dept2.pk)


class InventoryBulkEditTests(BulkEditBase):
    def setUp(self):
        super().setUp()
        self.items = [
            InventoryItem.objects.create(
                description=f'Item {i}', category=self.cat, unit=self.unit,
                location=self.loc, unit_cost=Decimal('10'),
            ) for i in range(2)
        ]

    def test_bulk_edit_reorder_level(self):
        self.client.force_login(self.finance)
        self.client.post(
            reverse('inventory:inventory_bulk_edit'),
            {'item_ids': [str(i.pk) for i in self.items], 'apply': '1',
             'location': '', 'reorder_level': '9'},
        )
        for i in self.items:
            i.refresh_from_db()
            self.assertEqual(i.reorder_level, 9)
