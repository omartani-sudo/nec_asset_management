# -*- coding: utf-8 -*-
from django.urls import path
from .views import lists_home, add_category, add_department, add_location, add_status, add_unit

app_name = 'lists'
urlpatterns = [
    path('', lists_home, name='lists_home'),
    path('category/add/', add_category, name='add_category'),
    path('department/add/', add_department, name='add_department'),
    path('location/add/', add_location, name='add_location'),
    path('status/add/', add_status, name='add_status'),
    path('unit/add/', add_unit, name='add_unit'),
]
