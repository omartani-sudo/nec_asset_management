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
        self.finance = User.objects.create_user(
            username='finance', email='finance@example.com', password='financepass123', role='finance'
        )
        self.viewer = User.objects.create_user(
            username='viewer', email='viewer@example.com', password='viewerpass123', role='viewer'
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

    def test_finance_cannot_escalate_own_role(self):
        self.client.force_login(self.finance)
        response = self.client.patch(
            reverse('user-detail', args=[self.finance.id]),
            {'role': 'admin'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_finance_cannot_update_other_users(self):
        self.client.force_login(self.finance)
        response = self.client.patch(
            reverse('user-detail', args=[self.admin.id]),
            {'username': 'pwned'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_viewer_user_list_omits_pii(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
        first = response.json()[0]
        self.assertNotIn('email', first)
        self.assertNotIn('phone', first)

    def test_refresh_token_is_single_use(self):
        login = self.client.post(reverse('api-login'), {'username': 'admin', 'password': 'adminpass123'})
        self.assertEqual(login.status_code, 200)
        refresh = login.json()['refresh']
        first = self.client.post(reverse('api-token-refresh'), {'refresh': refresh})
        self.assertEqual(first.status_code, 200)
        second = self.client.post(reverse('api-token-refresh'), {'refresh': refresh})
        self.assertEqual(second.status_code, 401)

    def test_inactive_user_token_rejected(self):
        login = self.client.post(reverse('api-login'), {'username': 'viewer', 'password': 'viewerpass123'})
        self.assertEqual(login.status_code, 200)
        token = login.json()['access']
        self.viewer.is_active = False
        self.viewer.save()
        response = self.client.get(reverse('fixedasset-list'), HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 401)
