# -*- coding: utf-8 -*-
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from nec_asset_management.settings.base import IsAdminUser, IsFinanceOrAdmin, IsViewerOrAbove
from .models import InventoryItem
from .serializers import InventoryItemSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related('category', 'unit', 'location', 'created_by', 'updated_by').all()
    serializer_class = InventoryItemSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFinanceOrAdmin()]
        return [IsViewerOrAbove()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
