# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def admin_required(list_url_name):
    """Allow only the admin role; redirect others to the given list view.

    Used to gate destructive actions (delete) in the web UI.
    Place under @login_required so unauthenticated users hit login first.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if getattr(request.user, 'role', None) != 'admin':
                messages.error(request, 'You do not have permission to perform this action.')
                return redirect(list_url_name)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def finance_admin_required(list_url_name):
    """Allow only admin/finance roles; redirect others to the given list view.

    Web counterpart of the API's IsFinanceOrAdmin permission — used for
    create/update/bulk edit actions. Place under @login_required.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if getattr(request.user, 'role', None) not in ('admin', 'finance'):
                messages.error(request, 'You do not have permission to perform this action.')
                return redirect(list_url_name)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
