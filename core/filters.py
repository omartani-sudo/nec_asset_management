# -*- coding: utf-8 -*-
"""Shared helpers for list filtering, sorting and pagination links."""
from django.utils.http import urlencode


def query_string(params, exclude=('page',)):
    """Build a URL-encoded query string from request params, minus exclusions."""
    return urlencode({k: v for k, v in params.items()
                      if k not in exclude and v not in (None, '')})


def apply_sort(qs, params, sort_map, default_order):
    """Apply a whitelisted sort key/direction from GET params.

    Never order by raw user input — unknown keys fall back to the
    model's default ordering.
    """
    key = params.get('sort', '')
    direction = params.get('dir', '')
    if key in sort_map:
        field = ('-' if direction == 'desc' else '') + sort_map[key]
        qs = qs.order_by(field)
    else:
        qs = qs.order_by(*default_order)
    return qs


def page_range(page_obj, on_each_side=1, on_ends=1):
    """Elided page range for the shared pagination include."""
    return page_obj.paginator.get_elided_page_range(
        page_obj.number, on_each_side=on_each_side, on_ends=on_ends
    )
