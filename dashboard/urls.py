
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # /dashboard/
    path('', views.dashboard_home, name='dashboard_home'),

    # /dashboard/login/
    path('login/', views.dashboard_login, name='dashboard_login'),

    # ex: /dashboard/submit-questions/
    path('<slug:page>/', views.dashboard_page, name='dashboard_page'),

    # ex: /dashboard/action/save-questions/
    path('action/<slug:action>', views.dashboard_action, name='dashboard_action'),
]