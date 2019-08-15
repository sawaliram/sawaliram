
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.DashboardHome.as_view(), name='home'),
    path('question/submit', views.SubmitQuestionsView.as_view(), name='submit-questions'),
    path('question/validate-new', views.ValidateNewExcelSheet.as_view(), name='validate-new-excel-sheet'),
    path('question/validate-curated', views.ValidateCuratedExcelSheet.as_view(), name='validate-curated-excel-sheet'),
    path('question/curate', views.CurateDataset.as_view(), name='curate-dataset'),
    path('manage-content', views.ManageContentView.as_view(), name='manage-content'),
    path('view-questions', views.ViewQuestionsView.as_view(), name='view-questions'),

    # task pages
    # these URLs point to a task page, like submit-questions
    path('answer-questions-list', views.get_answer_questions_list_view, name='answer-questions-list-view'),
    path('answer-questions/<int:question_id>/', views.get_answer_question_view, name='answer-question'),

    # action URLs
    # these URLs perform an action, like submitting a question
    # they are generally called from a form action
    path('action/submit-answer', views.submit_answer, name='submit-answer'),

]
