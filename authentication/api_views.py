# -*- coding: utf-8 -*-
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserLimitedSerializer, UserCreateSerializer, LoginSerializer, ChangePasswordSerializer
from .throttles import LoginRateThrottle
from nec_asset_management.settings.base import IsAdminUser, IsViewerOrAbove

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['list', 'retrieve']:
            # PII (email, phone) is only visible to admin/finance roles
            role = getattr(self.request.user, 'role', None)
            if role in ('admin', 'finance'):
                return UserSerializer
            return UserLimitedSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action in ['list', 'retrieve']:
            return [IsViewerOrAbove()]
        if self.action in ['update', 'partial_update']:
            # Admin-only: a finance user must not be able to promote themselves
            # (or demote/tamper with other accounts) via a PATCH on the role field.
            return [IsAdminUser()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsViewerOrAbove()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny()],
            throttle_classes=[LoginRateThrottle])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user is not None:
            login(request, user)
            return Response({'status': 'ok', 'user': UserSerializer(user).data})
        return Response({'status': 'error', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'status': 'ok', 'message': 'Logged out'})

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'status': 'ok', 'message': 'Password changed successfully.'})
