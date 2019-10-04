"""Define the urls that are part of the public website"""

from django.urls import path
from . import views

app_name = 'public_website'

urlpatterns = [
    path('user/<int:user_id>', views.UserProfileView.as_view(), name='user-profile'),
    path('', views.HomeView.as_view(), name='home'),
    path('get-involved', views.GetInvolvedView.as_view(), name='get-involved'),
    path('search', views.SearchView.as_view(), name='search')
]
