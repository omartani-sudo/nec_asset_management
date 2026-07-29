# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CurrentAssetViewSet

router = DefaultRouter()
router.register(r'current-assets', CurrentAssetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
