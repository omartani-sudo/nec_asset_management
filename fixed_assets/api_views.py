# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from nec_asset_management.settings.base import IsAdminUser, IsFinanceOrAdmin, IsViewerOrAbove
from .models import FixedAsset, DepreciationSchedule
from .serializers import FixedAssetSerializer, DepreciationScheduleSerializer


class FixedAssetViewSet(viewsets.ModelViewSet):
    queryset = FixedAsset.objects.select_related('category', 'department', 'location', 'status', 'assigned_to', 'created_by', 'updated_by').all()
    serializer_class = FixedAssetSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'bulk_delete']:
            return [IsAdminUser()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsFinanceOrAdmin()]
        return [IsViewerOrAbove()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({'error': '"ids" must be a list of asset IDs.'}, status=status.HTTP_400_BAD_REQUEST)
        ids = [i for i in ids if isinstance(i, int) and not isinstance(i, bool)]
        count = FixedAsset.objects.filter(pk__in=ids).count()
        with transaction.atomic():
            FixedAsset.objects.filter(pk__in=ids).delete()
        return Response({'deleted': count})


class DepreciationScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepreciationScheduleSerializer

    def get_permissions(self):
        return [IsViewerOrAbove()]

    def get_queryset(self):
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            return DepreciationSchedule.objects.filter(asset__asset_id=asset_id).select_related('asset').order_by('year_number')
        return DepreciationSchedule.objects.select_related('asset').all().order_by('asset', 'year_number')
