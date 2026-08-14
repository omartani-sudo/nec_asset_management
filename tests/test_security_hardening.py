# -*- coding: utf-8 -*-
"""Tests for login lockouts (web + admin) and security headers."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class SecurityHardeningTests(TestCase):
    def setUp(self):
        cache.clear()  # lockout counters persist across tests in LocMemCache
        self.client = Client()
        self.user = User.objects.create_user(username='target', password='correct-pass-123')

    def test_web_login_locks_out_with_429_after_five_failures(self):
        for i in range(5):
            resp = self.client.post(
                reverse('authentication:login'),
                {'username': 'target', 'password': f'wrong{i}'},
            )
            self.assertEqual(resp.status_code, 200)
        # 6th attempt: locked out with 429
        resp = self.client.post(
            reverse('authentication:login'),
            {'username': 'target', 'password': 'wrong6'},
        )
        self.assertEqual(resp.status_code, 429)
        self.assertContains(resp, 'Too many failed login attempts', status_code=429)

    def test_web_login_success_resets_failure_counter(self):
        for i in range(4):
            self.client.post(reverse('authentication:login'),
                             {'username': 'target', 'password': f'wrong{i}'})
        # Correct login succeeds
        resp = self.client.post(reverse('authentication:login'),
                                {'username': 'target', 'password': 'correct-pass-123'})
        self.assertRedirects(resp, reverse('dashboard:dashboard'))

    def test_security_headers_present(self):
        resp = self.client.get(reverse('health_check'))
        self.assertIn('Content-Security-Policy', resp.headers)
        self.assertIn('frame-ancestors', resp.headers['Content-Security-Policy'])
        self.assertIn('Permissions-Policy', resp.headers)

    def test_admin_login_locks_out_with_429(self):
        for i in range(5):
            resp = self.client.post('/admin/login/', {'username': 'admin', 'password': f'bad{i}'})
            self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/admin/login/', {'username': 'admin', 'password': 'bad6'})
        self.assertEqual(resp.status_code, 429)
