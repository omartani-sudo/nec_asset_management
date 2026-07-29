# -*- coding: utf-8 -*-
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import CurrentAsset
from .serializers import CurrentAssetSerializer


class CurrentAssetViewSet(viewsets.ModelViewSet):
    queryset = CurrentAsset.objects.select_related('category', 'department', 'location', 'status', 'created_by', 'updated_by').all()
    serializer_class = CurrentAssetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
