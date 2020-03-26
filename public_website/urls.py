"""Define the urls that are part of the public website"""

from django.urls import path
from . import views

app_name = 'public_website'

urlpatterns = [
    path('user/<int:user_id>/profile', views.UserProfileView.as_view(), name='user-profile'),
    path('update-organisation-info', views.UpdateOrganisationInfo.as_view(), name='update-organisation-info'),
    path('update-user-password', views.UpdateUserPassword.as_view(), name='update-user-password'),
    path('update-user-name', views.UpdateUserName.as_view(), name='update-user-name'),
    path('get-profile-pictures-form', views.GetProfilePictureOptions.as_view(), name='get-profile-picture-options'),
    path('update-profile-picture', views.UpdateProfilePicture.as_view(), name='update-profile-picture'),
    path('', views.HomeView.as_view(), name='home'),
    path('get-involved', views.GetInvolvedView.as_view(), name='get-involved'),
    path('research', views.ResearchPage.as_view(), name='research'),
    path('faq', views.FAQPage.as_view(), name='faq'),
    path('search', views.SearchView.as_view(), name='search'),
    path('view-notification', views.ViewNotification.as_view(), name='view-notification'),
    path('question/<int:question_id>/view-answer/<int:answer_id>', views.ViewAnswer.as_view(), name='view-answer'),
    path('question/<int:question_id>/answers/<int:answer_id>/user-comment/add', views.SubmitUserCommentOnAnswer.as_view(), name='submit-user-comment-answer'),
    path('question/<int:question_id>/answers/<int:answer_id>/user-comment/<int:comment_id>/delete', views.DeleteUserCommentOnAnswer.as_view(), name='delete-user-comment-answer'),
    path('article/<int:article>/', views.ArticleView.as_view(), name='view-article'),
    path('article/<str:slug>-<int:article>', views.ArticleView.as_view(), name='view-article'),
    path('lang/<str:language>', views.SetLanguageView.as_view(), name='set-language'),
    path('about', views.About.as_view(), name='about'),
]
