# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HealthCheckTests(TestCase):
    def test_health_check(self):
        client = Client()
        response = client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')


class APITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123', role='admin'
        )
        self.user = User.objects.create_user(
            username='user', email='user@example.com', password='userpass123', role='user'
        )

    def test_login_success(self):
        response = self.client.post(reverse('api-login'), {'username': 'admin', 'password': 'adminpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())

    def test_login_failure(self):
        response = self.client.post(reverse('api-login'), {'username': 'admin', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 401)

    def test_fixed_assets_requires_auth(self):
        response = self.client.get(reverse('fixedasset-list'))
        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_user(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-list'), {
            'username': 'newuser', 'password': 'newpass123', 'password2': 'newpass123', 'role': 'user'
        })
        self.assertEqual(response.status_code, 201)

    def test_user_cannot_create_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('user-list'), {
            'username': 'newuser', 'password': 'newpass123', 'password2': 'newpass123', 'role': 'user'
        })
        self.assertEqual(response.status_code, 403)
