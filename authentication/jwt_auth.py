# -*- coding: utf-8 -*-
"""JWT authentication with an active-account check on every request."""
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class NecJWTAuthentication(JWTAuthentication):
    """Same as simplejwt's JWTAuthentication, but rejects tokens belonging
    to deactivated accounts instead of trusting the token blindly."""
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if user is not None and not user.is_active:
            raise AuthenticationFailed('User account is disabled.', code='user_inactive')
        return user
