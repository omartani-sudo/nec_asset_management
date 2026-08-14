# -*- coding: utf-8 -*-
"""Tests for list filters, sorting and pagination."""
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status, Unit
from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem

User = get_user_model()


class ListFiltersPaginationBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.client.force_login(self.admin)

        self.cat_a = Category.objects.create(name='Alpha', code='ALP')
        self.cat_b = Category.objects.create(name='Bravo', code='BRA')
        self.dept_a = Department.objects.create(name='Finance')
        self.dept_b = Department.objects.create(name='HR')
        self.loc_a = Location.objects.create(name='HQ')
        self.status_a = Status.objects.create(name='In Use')
        self.status_b = Status.objects.create(name='Damaged')
        self.unit = Unit.objects.create(name='Piece')

        # 30 fixed assets across two categories/departments
        for i in range(30):
            FixedAsset.objects.create(
                asset_name=f'Asset {i:02d}',
                category=self.cat_a if i % 2 == 0 else self.cat_b,
                department=self.dept_a if i % 3 != 0 else self.dept_b,
                location=self.loc_a,
                status=self.status_a,
                purchase_date=date(2024, 1, 1) + timedelta(days=i),
                purchase_cost=Decimal('1000') + i,
                useful_life=5,
            )


class FixedAssetFilterTests(ListFiltersPaginationBase):
    def test_pagination_25_per_page(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['page_obj']), 25)
        self.assertEqual(resp.context['page_obj'].paginator.count, 30)

    def test_page_2_shows_remaining_5(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'page': 2})
        self.assertEqual(len(resp.context['page_obj']), 5)
        self.assertContains(resp, 'asset-check', count=5)

    def test_invalid_page_falls_back_to_page_1(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'page': 'banana'})
        self.assertEqual(resp.context['page_obj'].number, 1)

    def test_filter_by_category(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'category': self.cat_a.pk})
        self.assertEqual(resp.context['page_obj'].paginator.count, 15)

    def test_filter_by_department_and_search(self):
        resp = self.client.get(
            reverse('fixed_assets:fixed_asset_list'),
            {'department': self.dept_b.pk, 'q': 'Asset 03'},
        )
        qs = resp.context['page_obj'].paginator.object_list
        self.assertTrue(all(a.department_id == self.dept_b.pk for a in qs))

    def test_filter_by_status(self):
        FixedAsset.objects.filter(pk__in=FixedAsset.objects.values_list('pk', flat=True)[:5]).update(status=self.status_b)
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'status': self.status_b.pk})
        self.assertEqual(resp.context['page_obj'].paginator.count, 5)

    def test_date_range_filter(self):
        resp = self.client.get(
            reverse('fixed_assets:fixed_asset_list'),
            {'date_from': '2024-01-05', 'date_to': '2024-01-15'},
        )
        qs = resp.context['page_obj'].paginator.object_list
        self.assertTrue(all(date(2024, 1, 5) <= a.purchase_date <= date(2024, 1, 15) for a in qs))

    def test_sort_by_cost_desc(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'sort': 'cost', 'dir': 'desc'})
        first = resp.context['page_obj'][0]
        self.assertEqual(first.purchase_cost, Decimal('1029'))

    def test_invalid_sort_key_falls_back_to_default(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'sort': 'evil; DROP TABLE'})
        self.assertEqual(resp.status_code, 200)

    def test_pagination_link_preserves_filters(self):
        resp = self.client.get(reverse('fixed_assets:fixed_asset_list'), {'q': 'Asset 0'})
        self.assertContains(resp, 'q=Asset+0')


class CurrentAssetFilterTests(ListFiltersPaginationBase):
    def setUp(self):
        super().setUp()
        for i in range(5):
            CurrentAsset.objects.create(
                description=f'Cash {i}',
                category=self.cat_a,
                department=self.dept_a,
                location=self.loc_a,
                status=self.status_a,
                date_recorded=date(2024, 2, 1) + timedelta(days=i),
                value=Decimal('500'),
            )

    def test_search_and_status_filter(self):
        resp = self.client.get(
            reverse('current_assets:current_asset_list'),
            {'q': 'Cash 1', 'status': self.status_a.pk},
        )
        self.assertGreaterEqual(resp.context['page_obj'].paginator.count, 1)
        self.assertTrue(all('Cash' in a.description for a in resp.context['page_obj']))


class InventoryFilterTests(ListFiltersPaginationBase):
    def setUp(self):
        super().setUp()
        InventoryItem.objects.create(
            description='Low stock', category=self.cat_a, unit=self.unit,
            location=self.loc_a, unit_cost=Decimal('10'),
            opening_stock=2, reorder_level=5,
        )
        InventoryItem.objects.create(
            description='Empty', category=self.cat_a, unit=self.unit,
            location=self.loc_a, unit_cost=Decimal('10'),
            opening_stock=0, reorder_level=5,
        )
        InventoryItem.objects.create(
            description='Plenty', category=self.cat_b, unit=self.unit,
            location=self.loc_a, unit_cost=Decimal('10'),
            opening_stock=50, reorder_level=5,
        )

    def test_stock_status_reorder_filter(self):
        resp = self.client.get(reverse('inventory:inventory_list'), {'stock_status': 'reorder'})
        names = [i.description for i in resp.context['page_obj']]
        self.assertEqual(names, ['Low stock'])

    def test_stock_status_out_filter(self):
        resp = self.client.get(reverse('inventory:inventory_list'), {'stock_status': 'out'})
        names = [i.description for i in resp.context['page_obj']]
        self.assertEqual(names, ['Empty'])

    def test_balance_sort(self):
        resp = self.client.get(reverse('inventory:inventory_list'), {'sort': 'balance', 'dir': 'desc'})
        self.assertEqual(resp.context['page_obj'][0].description, 'Plenty')
