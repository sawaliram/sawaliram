"""Define the urls that are part of the public website"""

from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'public_website'

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/', permanent=False), name='home'),
    path('user/<int:user_id>', views.UserProfileView.as_view(), name='user-profile'),
    # path('', views.HomeView.as_view(), name='home')
]
