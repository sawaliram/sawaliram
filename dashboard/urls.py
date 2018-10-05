
from django.urls import path
from . import views

urlpatterns = [
    # /dashboard/
    path('', views.dashboard_home, name='dashboard_home'),

    # /dashboard/login/
    path('login/', views.dashboard_login, name='dashboard_login'),

    # ex: /dashboard/volunteer/
    path('<role>/', views.dashboard_role, name='dashboard_role'),

    # ex: /dashboard/volunteer/submit-questions/
    path('<role>/<action>/', views.dashboard_action, name='dashboard_action'),
]