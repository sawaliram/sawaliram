
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.DashboardHome.as_view(), name='home'),
    path('question/submit', views.SubmitQuestionsView.as_view(), name='submit-questions'),
    path('question/validate-new', views.ValidateNewExcelSheet.as_view(), name='validate-new-excel-sheet'),
    path('question/validate-curated', views.ValidateCuratedExcelSheet.as_view(), name='validate-curated-excel-sheet'),
    path('question/curate', views.CurateDataset.as_view(), name='curate-dataset'),
    path('question/<int:question_id>/answer/new', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('manage-content', views.ManageContentView.as_view(), name='manage-content'),
    path('view-questions', views.ViewQuestionsView.as_view(), name='view-questions'),
    path('answer-questions', views.AnswerQuestionsView.as_view(), name='answer-questions'),
]
