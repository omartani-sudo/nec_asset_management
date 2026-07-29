# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, DepartmentViewSet, LocationViewSet, StatusViewSet, UnitViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'units', UnitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
