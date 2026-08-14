# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class InventoryItem(models.Model):
    item_code = models.CharField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=200)
    category = models.ForeignKey('lists.Category', on_delete=models.PROTECT, related_name='inventory_items')
    unit = models.ForeignKey('lists.Unit', on_delete=models.PROTECT, related_name='inventory_items')
    opening_stock = models.PositiveIntegerField(default=0)
    received_qty = models.PositiveIntegerField(default=0)
    issued_qty = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=0)
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey('lists.Location', on_delete=models.PROTECT, related_name='inventory_items')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_inventory')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_inventory')

    class Meta:
        ordering = ['item_code', 'description']

    def __str__(self):
        return f"{self.item_code} - {self.description}"

    @property
    def balance_qty(self):
        return self.opening_stock + self.received_qty - self.issued_qty

    @property
    def total_value(self):
        return self.balance_qty * self.unit_cost

    @property
    def stock_status(self):
        if self.balance_qty == 0:
            return "Out of Stock"
        elif self.balance_qty <= self.reorder_level:
            return "Reorder Needed"
        else:
            return "OK"

    def save(self, *args, **kwargs):
        if not self.item_code:
            prefix = 'ITM'
            last = InventoryItem.objects.count()
            seq = str(last + 1).zfill(5)
            self.item_code = f"{prefix}{seq}"
        super().save(*args, **kwargs)
