# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('finance', 'Finance'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey('lists.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
