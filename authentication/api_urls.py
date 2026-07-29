# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='api-login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='api-logout'),
]
