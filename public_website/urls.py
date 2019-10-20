"""Define the urls that are part of the public website"""

from django.urls import path
from . import views

app_name = 'public_website'

urlpatterns = [
    path('user/<int:user_id>', views.UserProfileView.as_view(), name='user-profile'),
    path('', views.HomeView.as_view(), name='home'),
    path('get-involved', views.GetInvolvedView.as_view(), name='get-involved'),
    path('search', views.SearchView.as_view(), name='search'),
    path('view-notification', views.ViewNotification.as_view(), name='view-notification'),
    path('question/<int:question_id>/view-answer/<int:answer_id>', views.ViewAnswer.as_view(), name='view-answer'),
    path('question/<int:question_id>/answers/<int:answer_id>/user-comment/add', views.SubmitUserCommentOnAnswer.as_view(), name='submit-user-comment-answer'),
    path('question/<int:question_id>/answers/<int:answer_id>/user-comment/<int:comment_id>/delete', views.DeleteUserCommentOnAnswer.as_view(), name='delete-user-comment-answer'),
    path('about', views.AbputUs.as_view(), name='about'),
]
