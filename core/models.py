# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Lightweight audit trail for asset create/update/delete and bulk ops.

    Written by core.signals (per-object create/update/delete) and by views
    for bulk operations. Never write to this from the admin — it is
    intentionally not registered.
    """
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('bulk_delete', 'Bulk Delete'),
        ('bulk_edit', 'Bulk Edit'),
        ('dispose', 'Dispose'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_entries',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.user or '?'} {self.action} {self.model_name} {self.object_repr}"
