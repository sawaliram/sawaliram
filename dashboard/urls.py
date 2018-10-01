
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_login, name='dashboard_login'),
]