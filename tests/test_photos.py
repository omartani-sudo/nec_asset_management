# -*- coding: utf-8 -*-
"""Tests for asset photo upload and authenticated media serving."""
import io
import tempfile
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from lists.models import Category, Department, Location, Status
from fixed_assets.models import FixedAsset

User = get_user_model()


def make_png_bytes():
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), color=(13, 110, 253)).save(buf, format='PNG')
    buf.seek(0)
    return buf.read()


class PhotoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass12345', role='admin')
        self.client.force_login(self.admin)

        self.cat = Category.objects.create(name='Cat', code='CAT')
        self.dept = Department.objects.create(name='Dept')
        self.loc = Location.objects.create(name='Loc')
        self.status = Status.objects.create(name='In Use')
        self.temp_media = tempfile.mkdtemp()

    def _post_asset(self, photo=None):
        data = {
            'asset_name': 'With photo', 'category': self.cat.pk,
            'department': self.dept.pk, 'location': self.loc.pk,
            'status': self.status.pk, 'purchase_date': '2024-01-01',
            'purchase_cost': '1000', 'useful_life': 5, 'salvage_value': '0',
            'depreciation_method': 'SL', 'condition': 'new', 'disposal_date': '',
            'serial_number': '', 'supplier': '', 'notes': '',
        }
        if photo:
            data['photo'] = photo
        return self.client.post(reverse('fixed_assets:fixed_asset_create'), data)

    def test_photo_upload(self):
        with override_settings(MEDIA_ROOT=self.temp_media):
            png = SimpleUploadedFile('photo.png', make_png_bytes(), content_type='image/png')
            resp = self._post_asset(photo=png)
            self.assertRedirects(resp, reverse('fixed_assets:fixed_asset_list'))
            asset = FixedAsset.objects.get(asset_name='With photo')
            self.assertTrue(asset.photo.name.startswith('asset_photos/'))
            self.assertTrue(asset.photo.storage.exists(asset.photo.name))

    def test_media_requires_login(self):
        from django.conf import settings
        with override_settings(MEDIA_ROOT=self.temp_media):
            png = SimpleUploadedFile('photo.png', make_png_bytes(), content_type='image/png')
            self._post_asset(photo=png)
            asset = FixedAsset.objects.get(asset_name='With photo')
            url = reverse('media_serve', args=[asset.photo.name])
            self.client.logout()
            resp = self.client.get(url)
            self.assertIn(resp.status_code, (302, 301))
            self.client.force_login(self.admin)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

    def test_media_traversal_blocked(self):
        resp = self.client.get(reverse('media_serve', args=['../../etc/passwd']))
        self.assertEqual(resp.status_code, 404)
