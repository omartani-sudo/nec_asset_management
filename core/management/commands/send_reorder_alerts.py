# -*- coding: utf-8 -*-
"""Email a reorder summary to admin/finance users.

Scheduled via cron on the VPS (see README / setup-cron.sh).
Items are de-duplicated via InventoryItem.last_alert_sent.
"""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db.models import F, ExpressionWrapper, IntegerField
from django.utils import timezone

from inventory.models import InventoryItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Send reorder email alerts for inventory items at or below their reorder level.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=7,
            help='Suppress repeats for items alerted within this many days (default 7).',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Ignore last_alert_sent and send for all due items.',
        )

    def handle(self, *args, **options):
        items = InventoryItem.objects.select_related('location').annotate(
            balance=ExpressionWrapper(
                F('opening_stock') + F('received_qty') - F('issued_qty'),
                output_field=IntegerField(),
            )
        ).filter(balance__lte=F('reorder_level'))

        cutoff = timezone.now() - timedelta(days=options['days'])
        due = [
            i for i in items
            if options['force']
            or i.last_alert_sent is None
            or i.last_alert_sent < cutoff
        ]
        if not due:
            self.stdout.write('No reorder alerts to send.')
            return

        recipients = list(
            User.objects.filter(role__in=['admin', 'finance'], is_active=True)
            .exclude(email__exact='')
            .values_list('email', flat=True)
        )
        if not recipients:
            self.stdout.write('No recipients with email configured; nothing sent.')
            return

        lines = [
            f'{i.item_code} | {i.description} | {i.location.name} | '
            f'balance {i.balance} | reorder level {i.reorder_level}'
            for i in due
        ]
        subject = f'NEC Reorder Alert: {len(due)} item(s) need reordering'
        body = 'The following inventory items need reordering:\n\n' + '\n'.join(lines)

        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
        except Exception as e:
            self.stderr.write(f'Email send failed: {e}')
            return

        # .update() bypasses post_save signals — no audit noise for the daily cron.
        InventoryItem.objects.filter(pk__in=[i.pk for i in due]).update(
            last_alert_sent=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(
            f'Sent {len(due)} reorder alerts to {len(recipients)} recipient(s).'
        ))
