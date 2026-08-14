# -*- coding: utf-8 -*-
from django.urls import path
from .views import audit_log

app_name = 'core'
urlpatterns = [
    path('', audit_log, name='audit_log'),
]
