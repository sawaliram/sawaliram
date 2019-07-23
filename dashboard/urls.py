
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.get_home_view, name='home'),

    # task pages
    # these URLs point to a task page, like submit-questions
    path('submit-questions', views.get_submit_questions_view, name='submit-questions-view'),
    path('submit-excel-sheet', views.get_submit_excel_sheet_view, name='submit-excel-sheet-view'),
    path('view-questions', views.get_view_questions_view, name='view-questions-view'),
    path('answer-questions-list', views.get_answer_questions_list_view, name='answer-questions-list-view'),
    path('answer-questions/<int:question_id>/', views.get_answer_question_view, name='answer-question'),
    path('curate-data', views.get_curate_data_view, name='curate-data-view'),
    path('encode-data', views.get_encode_data_view, name='encode-data-view'),

    # action URLs
    # these URLs perform an action, like submitting a question
    # they are generally called from a form action
    path('action/submit-questions', views.submit_questions, name='submit-questions'),
    path('action/submit-excel-sheet', views.submit_excel_sheet, name='submit-excel-sheet'),
    path('action/submit-curated-dataset', views.submit_curated_dataset, name='submit-curated-dataset'),
    path('action/submit-encoded-dataset', views.submit_encoded_dataset, name='submit-encoded-dataset'),
    path('action/submit-answer', views.submit_answer, name='submit-answer'),

]
