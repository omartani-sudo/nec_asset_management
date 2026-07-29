# -*- coding: utf-8 -*-
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.232', '192.169.169.44', 'DESKTOP-25CJHGD', '192.168.1.*', 'testserver']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nec_asset_management',
        'USER': 'nec_user',
        'PASSWORD': 'nec_secure_pass',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
    'http://192.168.1.232:8000',
    'http://192.169.169.44:8000',
    'http://DESKTOP-25CJHGD:8000',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
    'http://192.168.1.232:8000',
    'http://192.169.169.44:8000',
    'http://DESKTOP-25CJHGD:8000',
]


