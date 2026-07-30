# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta
import math

User = get_user_model()

def to_date(val):
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        from datetime import datetime
        return datetime.strptime(val, '%Y-%m-%d').date()
    return val

class FixedAsset(models.Model):
    DEPRECIATION_METHODS = (
        ('SL', 'Straight Line'),
        ('RB', 'Reducing Balance'),
    )
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('broken', 'Broken'),
    )

    asset_id = models.CharField(max_length=100, unique=True, blank=True)
    asset_name = models.CharField(max_length=200)
    category = models.ForeignKey('lists.Category', on_delete=models.PROTECT, related_name='fixed_assets')
    department = models.ForeignKey('lists.Department', on_delete=models.PROTECT, related_name='fixed_assets')
    location = models.ForeignKey('lists.Location', on_delete=models.PROTECT, related_name='fixed_assets')
    serial_number = models.CharField(max_length=100, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2)
    useful_life = models.PositiveIntegerField(help_text="Useful life in years")
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    depreciation_method = models.CharField(max_length=2, choices=DEPRECIATION_METHODS, default='SL')
    status = models.ForeignKey('lists.Status', on_delete=models.PROTECT, related_name='fixed_assets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_fixed_assets')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    disposal_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_fixed_assets')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_fixed_assets')

    class Meta:
        ordering = ['-purchase_date', 'asset_id']
        indexes = [
            models.Index(fields=['asset_id']),
            models.Index(fields=['category']),
            models.Index(fields=['department']),
            models.Index(fields=['location']),
            models.Index(fields=['status']),
            models.Index(fields=['purchase_date']),
            models.Index(fields=['condition']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.asset_id} - {self.asset_name}"

    def annual_depreciation(self):
        cost = Decimal(str(self.purchase_cost))
        salvage = Decimal(str(self.salvage_value))
        if self.depreciation_method == 'SL':
            return (cost - salvage) / self.useful_life
        else:
            return (cost - salvage) * (Decimal('2') / self.useful_life)

    def accumulated_depreciation(self, as_of_date=None):
        if as_of_date is None:
            as_of_date = timezone.now().date()
        pd = to_date(self.purchase_date)
        dd = to_date(self.disposal_date)
        if dd and dd <= as_of_date:
            return Decimal('0')
        years = Decimal(str((min(as_of_date, date.today()) - pd).days / 365.25))
        if self.depreciation_method == 'SL':
            return min(self.annual_depreciation() * years, Decimal(str(self.purchase_cost)) - Decimal(str(self.salvage_value)))
        else:
            nbv = Decimal(str(self.purchase_cost))
            acc = Decimal('0')
            for _ in range(int(years)):
                year_dep = (nbv - Decimal(str(self.salvage_value))) * (Decimal('2') / self.useful_life)
                if nbv - year_dep <= Decimal(str(self.salvage_value)):
                    year_dep = nbv - Decimal(str(self.salvage_value))
                acc += year_dep
                nbv -= year_dep
                if nbv <= Decimal(str(self.salvage_value)):
                    break
            return acc

    def net_book_value(self, as_of_date=None):
        return max(self.purchase_cost - self.accumulated_depreciation(as_of_date=as_of_date), self.salvage_value)

    def generate_asset_id(self):
        prefix = self.category.code
        name_part = self.asset_name[:3].upper()
        last = FixedAsset.objects.filter(category=self.category).count()
        seq = str(last + 1).zfill(4)
        return f"{prefix}-{name_part}-{seq}"

    def generate_schedules(self):
        """Generate depreciation schedules for the asset's useful life."""
        from datetime import date
        from dateutil.relativedelta import relativedelta

        # Clear existing schedules
        self.depreciation_schedules.all().delete()

        cost = Decimal(str(self.purchase_cost))
        salvage = Decimal(str(self.salvage_value))
        opening_nbv = cost
        accumulated = Decimal('0')

        for year in range(1, self.useful_life + 1):
            start = self.purchase_date + relativedelta(years=year - 1)
            end = self.purchase_date + relativedelta(years=year) - relativedelta(days=1)

            if self.depreciation_method == 'SL':
                annual = (cost - salvage) / self.useful_life
            else:
                annual = (opening_nbv - salvage) * (Decimal('2') / self.useful_life)
                if opening_nbv - annual < salvage:
                    annual = opening_nbv - salvage

            accumulated += annual
            closing_nbv = opening_nbv - annual

            DepreciationSchedule.objects.create(
                asset=self,
                year_number=year,
                start_date=start,
                end_date=end,
                opening_nbv=opening_nbv.quantize(Decimal('0.01')),
                annual_depreciation=annual.quantize(Decimal('0.01')),
                accumulated_depreciation=accumulated.quantize(Decimal('0.01')),
                closing_nbv=max(closing_nbv, salvage).quantize(Decimal('0.01')),
            )

            opening_nbv = closing_nbv

    def save(self, *args, **kwargs):
        if not self.asset_id:
            self.asset_id = self.generate_asset_id()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.generate_schedules()

class DepreciationSchedule(models.Model):
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name='depreciation_schedules')
    year_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    opening_nbv = models.DecimalField(max_digits=15, decimal_places=2)
    annual_depreciation = models.DecimalField(max_digits=15, decimal_places=2)
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2)
    closing_nbv = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('asset', 'year_number')
        ordering = ['asset', 'year_number']

    def __str__(self):
        return f"{self.asset.asset_id} - Year {self.year_number}"
