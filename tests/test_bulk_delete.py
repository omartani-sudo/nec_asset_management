# -*- coding: utf-8 -*-
"""Tests for bulk delete (web UI + API) and delete role-gating."""
import json
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status, Unit
from fixed_assets.models import FixedAsset, DepreciationSchedule
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem

User = get_user_model()


class BulkDeleteTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='adminpass123', role='admin')
        self.finance = User.objects.create_user(username='finance', password='financepass123', role='finance')
        self.viewer = User.objects.create_user(username='viewer', password='viewerpass123', role='viewer')

        self.category = Category.objects.create(name='Test Category', code='TST')
        self.department = Department.objects.create(name='Test Department')
        self.location = Location.objects.create(name='Test Location')
        self.status = Status.objects.create(name='In Use')
        self.unit = Unit.objects.create(name='Piece')

        self.fixed = [
            FixedAsset.objects.create(
                asset_name=f'Fixed {i}',
                category=self.category, department=self.department,
                location=self.location, status=self.status,
                purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000.00'),
                useful_life=5,
            )
            for i in range(3)
        ]
        self.current = [
            CurrentAsset.objects.create(
                description=f'Current {i}',
                category=self.category, department=self.department,
                location=self.location, status=self.status, value=Decimal('500.00'),
            )
            for i in range(3)
        ]
        self.inventory = [
            InventoryItem.objects.create(
                description=f'Item {i}',
                category=self.category, unit=self.unit,
                location=self.location, unit_cost=Decimal('10.00'),
            )
            for i in range(3)
        ]


class FixedAssetBulkDeleteWebTests(BulkDeleteTestBase):
    def test_admin_confirmation_page_lists_assets_without_deleting(self):
        self.client.force_login(self.admin)
        ids = [str(self.fixed[0].pk), str(self.fixed[1].pk)]
        resp = self.client.post(reverse('fixed_assets:fixed_asset_bulk_delete'), {'asset_ids': ids})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.fixed[0].asset_id)
        self.assertContains(resp, self.fixed[1].asset_id)
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_admin_confirm_deletes_assets_and_schedules(self):
        self.client.force_login(self.admin)
        target = [self.fixed[0], self.fixed[1]]
        ids = [str(a.pk) for a in target]
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_delete'),
            {'asset_ids': ids, 'confirm': '1'},
        )
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(FixedAsset.objects.count(), 1)
        self.assertEqual(
            DepreciationSchedule.objects.filter(asset__in=target).count(), 0,
            'Depreciation schedules should cascade-delete with their assets',
        )

    def test_finance_is_blocked_from_bulk_delete(self):
        self.client.force_login(self.finance)
        ids = [str(self.fixed[0].pk)]
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_delete'),
            {'asset_ids': ids, 'confirm': '1'},
        )
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_finance_is_blocked_from_single_delete(self):
        self.client.force_login(self.finance)
        resp = self.client.post(reverse('fixed_assets:fixed_asset_delete', args=[self.fixed[0].pk]))
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_viewer_is_blocked_from_bulk_delete(self):
        self.client.force_login(self.viewer)
        ids = [str(a.pk) for a in self.fixed]
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_bulk_delete'),
            {'asset_ids': ids, 'confirm': '1'},
        )
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_viewer_is_blocked_from_single_delete(self):
        self.client.force_login(self.viewer)
        resp = self.client.post(reverse('fixed_assets:fixed_asset_delete', args=[self.fixed[0].pk]))
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_empty_selection_shows_error(self):
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('fixed_assets:fixed_asset_bulk_delete'), {})
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_list_page_hides_delete_controls_from_viewer(self):
        self.client.force_login(self.viewer)
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'))
        self.assertNotContains(resp, 'Delete Selected')
        self.assertNotContains(resp, 'asset-check')
        self.assertNotContains(resp, 'fixed_asset_delete')

    def test_list_page_shows_delete_controls_to_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'))
        self.assertContains(resp, 'Delete Selected')
        self.assertContains(resp, 'asset-check')


class CurrentAssetBulkDeleteWebTests(BulkDeleteTestBase):
    def test_admin_bulk_delete_current_assets(self):
        self.client.force_login(self.admin)
        ids = [str(a.pk) for a in self.current[:2]]
        resp = self.client.post(
            reverse('current_assets:current_asset_bulk_delete'),
            {'asset_ids': ids, 'confirm': '1'},
        )
        self.assertRedirects(resp, reverse('current_assets:current_asset_list'))
        self.assertEqual(CurrentAsset.objects.count(), 1)

    def test_viewer_blocked(self):
        self.client.force_login(self.viewer)
        ids = [str(a.pk) for a in self.current]
        self.client.post(
            reverse('current_assets:current_asset_bulk_delete'),
            {'asset_ids': ids, 'confirm': '1'},
        )
        self.assertEqual(CurrentAsset.objects.count(), 3)


class InventoryBulkDeleteWebTests(BulkDeleteTestBase):
    def test_admin_bulk_delete_inventory_items(self):
        self.client.force_login(self.admin)
        ids = [str(i.pk) for i in self.inventory[:2]]
        resp = self.client.post(
            reverse('inventory:inventory_bulk_delete'),
            {'item_ids': ids, 'confirm': '1'},
        )
        self.assertRedirects(resp, reverse('inventory:inventory_list'))
        self.assertEqual(InventoryItem.objects.count(), 1)

    def test_viewer_blocked(self):
        self.client.force_login(self.viewer)
        ids = [str(i.pk) for i in self.inventory]
        self.client.post(
            reverse('inventory:inventory_bulk_delete'),
            {'item_ids': ids, 'confirm': '1'},
        )
        self.assertEqual(InventoryItem.objects.count(), 3)


class ApiBulkDeleteTests(BulkDeleteTestBase):
    def test_admin_can_bulk_delete_fixed_assets(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('fixedasset-bulk-delete'),
            data=json.dumps({'ids': [self.fixed[0].id, self.fixed[1].id]}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['deleted'], 2)
        self.assertEqual(FixedAsset.objects.count(), 1)

    def test_api_bulk_delete_current_assets(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('currentasset-bulk-delete'),
            data=json.dumps({'ids': [self.current[0].id]}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['deleted'], 1)

    def test_finance_gets_403_on_bulk_delete(self):
        self.client.force_login(self.finance)
        resp = self.client.post(
            reverse('fixedasset-bulk-delete'),
            data=json.dumps({'ids': [self.fixed[0].id]}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_finance_gets_403_on_single_delete(self):
        self.client.force_login(self.finance)
        resp = self.client.delete(reverse('fixedasset-detail', args=[self.fixed[0].id]))
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_api_bulk_delete_inventory(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('inventoryitem-bulk-delete'),
            data=json.dumps({'ids': [self.inventory[0].id]}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['deleted'], 1)

    def test_viewer_gets_403(self):
        self.client.force_login(self.viewer)
        resp = self.client.post(
            reverse('fixedasset-bulk-delete'),
            data=json.dumps({'ids': [self.fixed[0].id]}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FixedAsset.objects.count(), 3)

    def test_bad_payload_gets_400(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('fixedasset-bulk-delete'),
            data=json.dumps({'ids': 'not-a-list'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
