
from django.urls import path
from . import views
from django.conf.urls import handler500

app_name = 'dashboard'

urlpatterns = [

    path('', views.get_home_view, name='dashboard_home'),

    path('login/', views.get_login_view, name='login-view'),

    # task pages
    # these URLs point to a task page, like submit-questions
    path('submit-questions', views.get_submit_questions_view, name='submit-questions-view'),
    path('submit-excel-sheet', views.get_submit_excel_sheet_view, name='submit-excel-sheet-view'),
    path('view-questions', views.get_view_questions_view, name='view-questions-view'),

    # action URLs
    # these URLs perform an action, like submitting a question
    # they are generally called from a form action
    path('action/submit-questions', views.submit_questions, name='submit-questions'),
    path('action/submit-excel-sheet', views.submit_excel_sheet, name='submit-excel-sheet'),
]
