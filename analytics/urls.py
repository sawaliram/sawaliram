"""Define the urls that will be handled by the analytics app"""

from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

# Use cache:   path('', cache_page(60*60)(views.home)),

app_name = 'analytics'

urlpatterns = [

    path('', (views.home)),
]
