# -*- coding: utf-8 -*-
"""Security + audit middleware."""
import threading

from django.http import JsonResponse

_local = threading.local()


def get_current_user():
    return getattr(_local, 'user', None)


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.user = getattr(request, 'user', None)
        try:
            return self.get_response(request)
        finally:
            _local.user = None


class SecurityHeadersMiddleware:
    """CSP + Permissions-Policy (complements HSTS/XFO set in settings)."""

    CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "base-uri 'self'; form-action 'self'; object-src 'none'; frame-ancestors 'none'"
    )
    PERMISSIONS_POLICY = 'camera=(), microphone=(), geolocation=(), interest-cohort=()'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('Content-Security-Policy', self.CSP)
        response.setdefault('Permissions-Policy', self.PERMISSIONS_POLICY)
        return response


class AdminLoginLockoutMiddleware:
    """Brute-force brake for the publicly exposed Django admin login.

    Django admin has no built-in rate limiting; this mirrors the main
    web login lockout (5 failures per IP -> 15-minute lockout).
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_SECONDS = 15 * 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/login/') and request.method == 'POST':
            from django.core.cache import cache
            ip = request.META.get('REMOTE_ADDR', '')
            lock_key = f'admin_login_fail:{ip}'
            if cache.get(lock_key, 0) >= self.MAX_ATTEMPTS:
                return JsonResponse(
                    {'error': 'Too many failed login attempts. Please try again later.'},
                    status=429,
                )
            response = self.get_response(request)
            # 200 = form re-rendered (failure); 302 = successful login
            if response.status_code == 200:
                cache.set(lock_key, cache.get(lock_key, 0) + 1, self.LOCKOUT_SECONDS)
            else:
                cache.delete(lock_key)
            return response
        return self.get_response(request)
