
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
    path('answer-questions', views.AnswerQuestions.as_view(), name='answer-questions'),
    path('review-answers', views.ReviewAnswersList.as_view(), name='review-answers'),
    path('question/<int:question_id>/answers/<int:answer_id>/review', views.ReviewAnswerView.as_view(), name='review-answer'),
    path('question/<int:question_id>/answers/<int:answer_id>/approve', views.ApproveAnswerView.as_view(), name='approve-answer'),

    path('question/<int:question_id>/answers/<int:answer_id>/comment/add', views.AnswerCommentView.as_view(), name='submit-answer-comment'),
    path('question/<int:question_id>/answers/<int:answer_id>/comment/<int:comment_id>/delete', views.AnswerCommentDeleteView.as_view(), name='delete-answer-comment'),

    path('article/<int:draft_id>/edit/', views.EditArticleView.as_view(), name='edit-article'),
    path('article/<int:article>/delete', views.DeleteArticleView.as_view(), name='delete-article'),
    path('article/new/', views.create_article, name='create-article'),
    path('article/<int:article>/review/', views.ReviewSubmittedArticleView.as_view(), name='review-article'),
    path('article/<int:article>/approve/', views.ApproveSubmittedArticleView.as_view(), name='approve-article'),
    path('article/<int:article>/comment/add', views.AddArticleCommentView.as_view(), name='submit-article-comment'),
    path('article/<int:article>/comment/<int:comment_id>/delete/', views.DeleteArticleCommentView.as_view(), name='delete-article-comment'),

    path('article/<int:source>/translate/from/<str:lang_from>/to/<str:lang_to>', views.EditArticleTranslation.as_view(), name='edit-article-translation')

]
