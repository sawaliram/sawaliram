
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # /dashboard/
    path('', views.dashboard_home, name='dashboard_home'),

    # /dashboard/login/
    path('login/', views.dashboard_login, name='dashboard_login'),

    # ex: /dashboard/submit-questions/
    path('<slug:page>/', views.task_page, name='task_page'),

    # action URLs
    path('action/submit-questions', views.submit_questions, name='submit-questions'),
    path('action/submit-excel-sheet', views.work_in_progress, name='submit-excel-sheet'),
]