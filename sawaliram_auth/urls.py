"""Define the urls that will be handled by the user app"""

from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [

    path('', views.LoginView.as_view(), name='auth_root'),
    path('login', views.LoginView.as_view(), name='login'),
    path('signup', views.SignUpView.as_view(), name='signup'),
]
