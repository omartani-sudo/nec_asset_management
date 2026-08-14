# -*- coding: utf-8 -*-
"""Tests for the disposal workflow and schedule regeneration on edit."""
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status
from fixed_assets.models import FixedAsset, DepreciationSchedule

User = get_user_model()


class DisposalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.viewer = User.objects.create_user(username='viewer', password='pass12345', role='viewer')

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.dept = Department.objects.create(name='Dept')
        self.loc = Location.objects.create(name='Loc')
        self.status = Status.objects.create(name='In Use')

        self.asset = FixedAsset.objects.create(
            asset_name='To dispose', category=self.cat, department=self.dept,
            location=self.loc, status=self.status,
            purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000'),
            salvage_value=Decimal('100'), useful_life=5,
        )

    def test_dispose_sets_status_and_date(self):
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('fixed_assets:fixed_asset_dispose', args=[self.asset.pk]))
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_detail', args=[self.asset.pk]))
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status.name, 'Disposed')
        self.assertEqual(self.asset.disposal_date, date.today())

    def test_dispose_stops_depreciation(self):
        self.asset.disposal_date = date.today()
        self.asset.status = Status.objects.get_or_create(name='Disposed')[0]
        self.asset.save()
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.accumulated_depreciation(), Decimal('0'))
        self.assertEqual(self.asset.net_book_value(), Decimal('100'))

    def test_viewer_blocked_from_dispose(self):
        self.client.force_login(self.viewer)
        self.client.post(reverse('fixed_assets:fixed_asset_dispose', args=[self.asset.pk]))
        self.asset.refresh_from_db()
        self.assertIsNone(self.asset.disposal_date)

    def test_edit_financial_fields_regenerates_schedules(self):
        self.asset.refresh_from_db()
        original_rows = list(DepreciationSchedule.objects.filter(asset=self.asset).values())
        self.asset.useful_life = 10
        self.asset.save()
        self.assertEqual(DepreciationSchedule.objects.filter(asset=self.asset).count(), 10)
        self.assertNotEqual(
            list(DepreciationSchedule.objects.filter(asset=self.asset).values()), original_rows
        )

    def test_edit_status_only_keeps_schedules(self):
        self.asset.refresh_from_db()
        original_rows = list(DepreciationSchedule.objects.filter(asset=self.asset).values())
        self.asset.condition = 'poor'
        self.asset.save()
        self.assertEqual(
            list(DepreciationSchedule.objects.filter(asset=self.asset).values()), original_rows
        )
