"""Define the urls that will be handled by the user app"""

from django.urls import path
from . import views
from . import oauth

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
    path('oauth2/github', oauth.login_github, name='oauth-login-github'),
    path('oauth2/github/authorise', oauth.authorise_github, name='oauth-authorise-github'),
]
