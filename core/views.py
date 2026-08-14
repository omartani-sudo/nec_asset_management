# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import AuditLog
from .filters import query_string, page_range
from core.decorators import finance_admin_required


def health_check(request):
    """Public liveness probe. Deliberately terse: no deployment details
    (migration state, versions) leak to unauthenticated callers."""
    try:
        connection.ensure_connection()
        return JsonResponse({
            'status': 'ok',
            'message': 'All systems operational',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        message = str(e) if settings.DEBUG else 'Service temporarily unavailable'
        return JsonResponse({
            'status': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }, status=500)


@login_required
@finance_admin_required('dashboard:dashboard')
def audit_log(request):
    qs = AuditLog.objects.select_related('user').all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(object_repr__icontains=q) | Q(object_id__icontains=q))
    action = request.GET.get('action', '')
    if action:
        qs = qs.filter(action=action)
    model_name = request.GET.get('model_name', '')
    if model_name:
        qs = qs.filter(model_name=model_name)
    for key, lookup in (('date_from', 'timestamp__gte'), ('date_to', 'timestamp__lte')):
        val = request.GET.get(key, '')
        if val:
            try:
                dt = datetime.strptime(val, '%Y-%m-%d')
                if key == 'date_to':
                    dt = dt.replace(hour=23, minute=59, second=59)
                qs = qs.filter(**{lookup: dt})
            except ValueError:
                pass

    paginator = Paginator(qs, 50)
    page_obj = paginator.get_page(request.GET.get('page', '1'))
    context = {
        'entries': page_obj,
        'page_obj': page_obj,
        'query_string': query_string(request.GET),
        'page_range': page_range(page_obj),
        'actions': AuditLog.ACTION_CHOICES,
        'model_names': sorted(set(AuditLog.objects.values_list('model_name', flat=True))),
    }
    return render(request, 'core/audit_log.html', context)


@login_required
def serve_media(request, path):
    """Authenticated media serving (photos). Private site — no public URLs."""
    root = Path(settings.MEDIA_ROOT).resolve()
    file_path = (root / path).resolve()
    if not str(file_path).startswith(str(root)) or not file_path.is_file():
        raise Http404
    return FileResponse(file_path.open('rb'))
