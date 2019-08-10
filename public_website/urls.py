"""Define the urls that are part of the public website"""

from django.urls import path
from . import views

app_name = 'public_website'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home')
]
