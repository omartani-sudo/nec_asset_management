"""
URL configuration for nec_asset_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import health_check
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('health/', health_check, name='health_check'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('authentication.urls')),
    path('fixed-assets/', include('fixed_assets.urls')),
    path('current-assets/', include('current_assets.urls')),
    path('inventory/', include('inventory.urls')),
    path('reports/', include('reports.urls')),
    path('lists/', include('lists.urls')),
    path('api/auth/', include('authentication.api_urls')),
    path('api/fixed-assets/', include('fixed_assets.api_urls')),
    path('api/current-assets/', include('current_assets.api_urls')),
    path('api/inventory/', include('inventory.api_urls')),
    path('api/lists/', include('lists.api_urls')),
]
