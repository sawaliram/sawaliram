
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.get_home_view, name='dashboard_home'),

    path('login/', views.get_login_view, name='login-view'),
    path('signup/', views.get_signup_view, name='signup-view'),

    # task pages
    # these URLs point to a task page, like submit-questions
    path('submit-questions', views.get_submit_questions_view, name='submit-questions-view'),
    path('submit-excel-sheet', views.get_submit_excel_sheet_view, name='submit-excel-sheet-view'),
    path('view-questions', views.get_view_questions_view, name='view-questions-view'),
    path('answer-questions-list', views.get_answer_questions_list_view, name='answer-questions-list-view'),
    path('manage-data', views.get_manage_data_view, name='manage-data-view'),
    path('submit-curated-dataset', views.submit_curated_dataset, name='submit-curated-dataset'),

    # action URLs
    # these URLs perform an action, like submitting a question
    # they are generally called from a form action
    path('action/login-user', views.login_user, name='login-user'),
    path('action/logout-user', views.logout_user, name='logout-user'),
    path('action/signup-user', views.signup_user, name='signup-user'),
    path('action/submit-questions', views.submit_questions, name='submit-questions'),
    path('action/submit-excel-sheet', views.submit_excel_sheet, name='submit-excel-sheet'),
]