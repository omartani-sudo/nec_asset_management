# -*- coding: utf-8 -*-
"""Tests for the send_reorder_alerts management command."""
from decimal import Decimal

from django.test import TestCase, override_settings
from django.core import mail
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone

from lists.models import Category, Location, Unit
from inventory.models import InventoryItem

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReorderAlertTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='pass12345', role='admin', email='admin@nec.gov')
        self.finance = User.objects.create_user(
            username='finance', password='pass12345', role='finance', email='fin@nec.gov')
        self.admin_no_email = User.objects.create_user(
            username='noemail', password='pass12345', role='admin', email='')
        self.viewer = User.objects.create_user(
            username='viewer', password='pass12345', role='viewer', email='viewer@nec.gov')

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.loc = Location.objects.create(name='Loc')
        self.unit = Unit.objects.create(name='Piece')

        self.low = InventoryItem.objects.create(
            description='Low', category=self.cat, unit=self.unit,
            location=self.loc, unit_cost=Decimal('10'),
            opening_stock=2, reorder_level=5)
        self.ok = InventoryItem.objects.create(
            description='OK', category=self.cat, unit=self.unit,
            location=self.loc, unit_cost=Decimal('10'),
            opening_stock=50, reorder_level=5)

    def test_sends_to_admin_and_finance_with_email(self):
        call_command('send_reorder_alerts')
        self.assertEqual(len(mail.outbox), 1)
        recipients = mail.outbox[0].to
        self.assertIn('admin@nec.gov', recipients)
        self.assertIn('fin@nec.gov', recipients)
        self.assertNotIn('viewer@nec.gov', recipients)
        self.assertIn('Low', mail.outbox[0].body)
        self.assertNotIn('OK', mail.outbox[0].body)

    def test_dedup_via_last_alert_sent(self):
        call_command('send_reorder_alerts')
        self.assertEqual(len(mail.outbox), 1)
        call_command('send_reorder_alerts')
        self.assertEqual(len(mail.outbox), 1)  # no second email
        self.low.refresh_from_db()
        self.assertIsNotNone(self.low.last_alert_sent)

    def test_days_zero_resends(self):
        call_command('send_reorder_alerts')
        call_command('send_reorder_alerts', days=0)
        self.assertEqual(len(mail.outbox), 2)

    def test_no_due_items_no_mail(self):
        self.low.opening_stock = 99
        self.low.save()
        call_command('send_reorder_alerts')
        self.assertEqual(len(mail.outbox), 0)
