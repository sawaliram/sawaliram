"""Define the urls that will be handled by the user app"""

from django.urls import path
from . import views

app_name = 'sawaliram_auth'

urlpatterns = [

    path('', views.SigninView.as_view()),
    path('signin', views.SigninView.as_view(), name='signin'),
    path('signout', views.SignoutView.as_view(), name='signout'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('how-can-i-help', views.HowCanIHelpView.as_view(), name='how_can_i_help'),
    path('manage-users', views.ManageUsersView.as_view(), name='manage-users'),
    path('update-permissions', views.UpdateUserPermissions.as_view(), name='update-permissions'),
    path('grant-permission', views.GrantOrDenyUserPermission.as_view(), name='grant-permission'),
    path('bookmark/add', views.AddBookmark.as_view(), name='add-bookmark'),
    path('bookmark/remove', views.RemoveBookmark.as_view(), name='remove-bookmark'),
    path('bookmark/delete', views.DeleteBookmark.as_view(), name='delete-bookmark'),
    path('draft/remove', views.RemoveDraft.as_view(), name='remove-draft'),
    path('verify-email', views.VerifyEmailMessagesView.as_view(), name='verify-email-info'),
    path('verify/<str:verification_code>', views.VerifyEmailView.as_view(), name='verify-email'),
    path('reset-password', views.ResetPasswordView.as_view(), name='reset-password'),
    path('change-password-form/<str:password_reset_code>', views.ChangePasswordFormView.as_view(), name='change-password-form'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]
