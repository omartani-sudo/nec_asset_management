# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class CurrentAsset(models.Model):
    asset_id = models.CharField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=200)
    category = models.ForeignKey('lists.Category', on_delete=models.PROTECT, related_name='current_assets')
    department = models.ForeignKey('lists.Department', on_delete=models.PROTECT, related_name='current_assets')
    date_recorded = models.DateField(default=date.today)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    location = models.ForeignKey('lists.Location', on_delete=models.PROTECT, related_name='current_assets')
    status = models.ForeignKey('lists.Status', on_delete=models.PROTECT, related_name='current_assets')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_current_assets')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_current_assets')

    class Meta:
        ordering = ['-date_recorded', 'asset_id']

    def __str__(self):
        return f"{self.asset_id} - {self.description}"

    def save(self, *args, **kwargs):
        if not self.asset_id:
            prefix = 'CA'
            last = CurrentAsset.objects.count()
            seq = str(last + 1).zfill(5)
            self.asset_id = f"{prefix}{seq}"
        super().save(*args, **kwargs)
