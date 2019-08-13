"""Define the urls that are part of the public website"""

from django.urls import path
# from . import views
from django.views.generic import RedirectView

app_name = 'public_website'

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/', permanent=False), name='home'),
    # path('', views.HomeView.as_view(), name='home')
]
