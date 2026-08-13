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
