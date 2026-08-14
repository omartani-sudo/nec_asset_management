# -*- coding: utf-8 -*-
"""Thread-local access to the current request user (for audit signals)."""
import threading

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
