# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from io import StringIO


def health_check(request):
    try:
        connection.ensure_connection()

        from django.core.management import call_command
        output = StringIO()
        call_command('showmigrations', '--plan', stdout=output, no_color=True)
        migrations = output.getvalue()
        unapplied = [line for line in migrations.split('\n') if '[ ]' in line]

        if unapplied:
            return JsonResponse({
                'status': 'error',
                'message': 'Migrations not applied',
                'unapplied_migrations': len(unapplied),
                'timestamp': timezone.now().isoformat()
            }, status=500)

        return JsonResponse({
            'status': 'ok',
            'message': 'All systems operational',
            'database': 'connected',
            'migrations': 'applied',
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        from django.conf import settings
        message = str(e) if settings.DEBUG else 'Service temporarily unavailable'
        return JsonResponse({
            'status': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }, status=500)
