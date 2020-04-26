"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('article/', include('article.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('public_website.urls', namespace='public_site')),
    path('users/', include('sawaliram_auth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path('analytics/', include('analytics.urls')),
]

handler404 = 'dashboard.views.get_error_404_view'
