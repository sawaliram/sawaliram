
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
    path('translate/answers', views.TranslateAnswersList.as_view(), name='translate-answers'),
    path('review-answers', views.ReviewAnswersList.as_view(), name='review-answers'),
    path('question/<int:question_id>/answers/<int:answer_id>/review', views.ReviewAnswerView.as_view(), name='review-answer'),
    path('question/<int:question_id>/answers/<int:answer_id>/approve', views.ApproveAnswerView.as_view(), name='approve-answer'),
    path('question/<int:question>/answers/<int:answer>/comment/add', views.CreateAnswerCommentView.as_view(), { 'target_type': 'answer' }, name='submit-answer-comment'),

    path('comment/<int:pk>/delete', views.DeleteCommentView.as_view(), name='delete-comment'),

    path('article/<int:draft_id>/edit/', views.EditArticleView.as_view(), name='edit-article'),
    path('article/<int:article>/delete', views.DeleteArticleView.as_view(), name='delete-article'),
    path('article/new/', views.create_article, name='create-article'),
    path('article/<int:article>/review/', views.ReviewSubmittedArticleView.as_view(), name='review-article'),
    path('article/<int:article>/approve/', views.ApproveSubmittedArticleView.as_view(), name='approve-article'),

    path('article/<int:target>/comment/add', views.CreateCommentView.as_view(), { 'target_type': 'article' }, name='submit-article-comment'),
    path('article/<int:source>/translate', views.CreateArticleTranslation.as_view(), name='translate-article'),
    path('question/<int:source>/answer/<int:answer>/translate', views.CreateAnswerTranslation.as_view(), name='translate-answer'),
    path('article/<int:source>/translate/from/<str:lang_from>/to/<str:lang_to>', views.EditArticleTranslation.as_view(), name='edit-article-translation'),
    path('question/<int:source>/answer/<int:answer>/translate/from/<str:lang_from>/to/<str:lang_to>', views.EditAnswerTranslation.as_view(), name='edit-answer-translation'),

    path('translate/articles/<int:pk>/review', views.ReviewArticleTranslation.as_view(), name='review-article-translation'),
    path('translate/articles/<int:target>/comment/add', views.CreateCommentView.as_view(), { 'target_type': 'article-translation' }, name='submit-article-translation-comment'),
    path('translate/answers/<int:pk>/review', views.ReviewAnswerTranslation.as_view(), name='review-answer-translation'),
    path('translate/answers/<int:target>/comment/add', views.CreateCommentView.as_view(), { 'target_type': 'answer-translation' }, name='submit-answer-translation-comment'),

    path('translate/articles/<int:pk>/delete', views.DeleteArticleTranslation.as_view(), name='delete-article-translation'),
    path('translate/answers/<int:pk>/delete', views.DeleteAnswerTranslation.as_view(), name='delete-answer-translation'),
    path('translate/questions/<int:pk>/delete', views.DeleteQuestionTranslation.as_view(), name='delete-question-translation'),
]
