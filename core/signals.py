# -*- coding: utf-8 -*-
"""Audit-log signals for the asset models.

Records create/update/delete per object (including queryset bulk deletes,
which fire pre_delete per instance). Audit writes must NEVER break the real
operation, so every write is wrapped in try/except.
"""
import logging

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from fixed_assets.models import FixedAsset
from current_assets.models import CurrentAsset
from inventory.models import InventoryItem
from .models import AuditLog
from .middleware import get_current_user

logger = logging.getLogger('core.signals')

AUDITED_MODELS = (FixedAsset, CurrentAsset, InventoryItem)


@receiver(post_save)
def audit_post_save(sender, instance, created, update_fields, **kwargs):
    if sender not in AUDITED_MODELS:
        return
    action = 'create' if created else 'update'
    fields = list(update_fields or [])
    try:
        AuditLog.objects.create(
            user=get_current_user(),
            action=action,
            model_name=sender.__name__,
            object_repr=str(instance),
            object_id=str(instance.pk),
            details={'fields': fields},
        )
    except Exception:
        logger.exception('AuditLog write failed on %s %s', action, sender.__name__)


@receiver(pre_delete)
def audit_pre_delete(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return
    try:
        AuditLog.objects.create(
            user=get_current_user(),
            action='delete',
            model_name=sender.__name__,
            object_repr=str(instance),
            object_id=str(instance.pk),
        )
    except Exception:
        logger.exception('AuditLog write failed on delete %s', sender.__name__)
