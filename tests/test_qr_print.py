# -*- coding: utf-8 -*-
"""Tests for QR label printing (sheet + detail-page QR container)."""
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status
from fixed_assets.models import FixedAsset

User = get_user_model()


class QRPrintTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.viewer = User.objects.create_user(username='viewer', password='pass12345', role='viewer')

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.dept = Department.objects.create(name='Dept')
        self.loc = Location.objects.create(name='Loc')
        self.status = Status.objects.create(name='In Use')

        self.assets = [
            FixedAsset.objects.create(
                asset_name=f'QR {i}', category=self.cat, department=self.dept,
                location=self.loc, status=self.status,
                purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000'), useful_life=5,
            ) for i in range(2)
        ]

    def test_print_sheet_renders_selected_assets(self):
        self.client.force_login(self.viewer)  # printing allowed for all roles
        resp = self.client.post(
            reverse('fixed_assets:fixed_asset_print_qr'),
            {'asset_ids': [str(a.pk) for a in self.assets]},
        )
        self.assertEqual(resp.status_code, 200)
        for a in self.assets:
            self.assertContains(resp, a.asset_id)
        self.assertContains(resp, 'qrcode.min.js')
        self.assertContains(resp, 'testserver')  # absolute URLs embedded for the QR payload

    def test_print_sheet_requires_post_with_ids(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('fixed_assets:fixed_asset_print_qr'))
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
        resp = self.client.post(reverse('fixed_assets:fixed_asset_print_qr'), {})
        self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))

    def test_detail_page_has_qr_container(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('fixed_assets:fixed_asset_detail', args=[self.assets[0].pk]))
        self.assertContains(resp, 'asset-qr')
