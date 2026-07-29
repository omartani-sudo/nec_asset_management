# -*- coding: utf-8 -*-
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from nec_asset_management.settings.base import IsAdminUser, IsFinanceOrAdmin, IsViewerOrAbove
from .models import FixedAsset, DepreciationSchedule
from .serializers import FixedAssetSerializer, DepreciationScheduleSerializer


class FixedAssetViewSet(viewsets.ModelViewSet):
    queryset = FixedAsset.objects.select_related('category', 'department', 'location', 'status', 'assigned_to', 'created_by', 'updated_by').all()
    serializer_class = FixedAssetSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFinanceOrAdmin()]
        return [IsViewerOrAbove()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class DepreciationScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepreciationScheduleSerializer

    def get_permissions(self):
        return [IsViewerOrAbove()]

    def get_queryset(self):
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            return DepreciationSchedule.objects.filter(asset__asset_id=asset_id).select_related('asset').order_by('year_number')
        return DepreciationSchedule.objects.select_related('asset').all().order_by('asset', 'year_number')
