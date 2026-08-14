# -*- coding: utf-8 -*-
"""Tests for the dashboard department filter."""
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import Category, Department, Location, Status
from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset

User = get_user_model()


class DashboardFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.client.force_login(self.admin)

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.dept_a = Department.objects.create(name='Finance')
        self.dept_b = Department.objects.create(name='HR')
        self.loc = Location.objects.create(name='Loc')
        self.status = Status.objects.create(name='In Use')

        FixedAsset.objects.create(
            asset_name='Fin asset', category=self.cat, department=self.dept_a,
            location=self.loc, status=self.status,
            purchase_date=date(2024, 1, 1), purchase_cost=Decimal('1000'), useful_life=5)
        FixedAsset.objects.create(
            asset_name='HR asset', category=self.cat, department=self.dept_b,
            location=self.loc, status=self.status,
            purchase_date=date(2024, 1, 1), purchase_cost=Decimal('2000'), useful_life=5)
        CurrentAsset.objects.create(
            description='Fin cash', category=self.cat, department=self.dept_a,
            location=self.loc, status=self.status, value=Decimal('300'))

    def test_department_filter_scopes_kpis(self):
        resp = self.client.get(reverse('dashboard:dashboard'), {'department': self.dept_a.pk})
        self.assertEqual(resp.status_code, 200)
        ctx = resp.context
        self.assertEqual(ctx['total_fixed'], 1)
        self.assertEqual(ctx['total_purchase_cost'], 1000.0)
        self.assertEqual(ctx['total_current'], 300.0)
        self.assertEqual(ctx['selected_department'], self.dept_a)

    def test_no_filter_returns_all(self):
        resp = self.client.get(reverse('dashboard:dashboard'))
        ctx = resp.context
        self.assertEqual(ctx['total_fixed'], 2)
        self.assertIsNone(ctx['selected_department'])

    def test_invalid_department_is_404(self):
        resp = self.client.get(reverse('dashboard:dashboard'), {'department': '99999'})
        self.assertEqual(resp.status_code, 404)

    def test_department_dropdown_present(self):
        resp = self.client.get(reverse('dashboard:dashboard'))
        self.assertContains(resp, 'All Departments')
        self.assertContains(resp, 'Finance')
