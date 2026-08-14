# -*- coding: utf-8 -*-
"""API throttles for authentication endpoints."""
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Tight per-IP limit on credential attempts — brute-force brake.

    Applied to the JWT login endpoint and the session login action, so a
    single IP gets 5 attempts per minute instead of the global 100/day.
    """
    rate = '5/min'
