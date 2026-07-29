# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', UserViewSet.as_view({'post': 'login'}), name='api-login'),
    path('auth/logout/', UserViewSet.as_view({'post': 'logout'}), name='api-logout'),
]
