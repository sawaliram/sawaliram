from authlib.integrations.django_client import OAuth

from django.dispatch import receiver
from authlib.integrations.django_client import token_update

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, reverse
from django.contrib.auth import login
from .models import User, OAuth2Token


def fetch_token(name, request):
    model = OAuth2Token

    tokens = model.objects.filter(
        name=name,
        user=request.user,
    )

    return tokens[0].to_token()


oauth = OAuth(fetch_token=fetch_token)



@receiver(token_update)
def on_token_update(sender, token, refresh_token=None, access_token=None, **kwargs):
    if refresh_token:
        item = OAuth2Token.objects.get(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.objects.get(name=name, access_token=access_token)
    else:
        return

    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    item.save()


if 'github' in settings.AUTHLIB_OAUTH_CLIENTS:

    oauth.register(
        name='github',
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

client_kwargs = {
    'scope': 'profile',
    'token_endpoint_auth_method': 'client_secret_basic',
    'token_placement': 'header',
}

def login_github(request):
    if not hasattr(oauth, 'github'):
        # GitHub login not enabled for server
        raise Http404

    # build a full authorize callback uri
    redirect_uri = request.build_absolute_uri('/users/oauth2/github/authorise')
    return oauth.github.authorize_redirect(request, redirect_uri)

def authorise_github(request):
    if not hasattr(oauth, 'github'):
        # GitHub login not enabled for server
        raise Http404

    token = oauth.github.authorize_access_token(request)

    # find out primary email
    emails = oauth.github.get('/user/emails', token=token).json()

    for e in emails:
        if e.get('primary'):
            # TODO: check e.get('verified')
            primary_email = e.get('email')

    # get or create matching user

    try:
        u = User.objects.get(email=primary_email)
    except User.DoesNotExist:
        # fetch user data
        profile = oauth.github.get('/user', token=token).json()

        # figure out first and last name
        split_name = profile.get('name').split(' ')
        first_name = split_name[0]
        if len(split_name) == 1:
            last_name = ''
        else:
            last_name = split_name[1:]

        # check organisation
        org = profile.get('company')
        if not org: org = ''

        # create the user object
        u = User.objects.create_user(
            email=primary_email,
            first_name=first_name,
            last_name=last_name,
            organisation=org,
            password=None,
        )

    # mark the user as logged in
    login(request, u)

    # save token to database

    t = OAuth2Token()
    t.name = 'github',
    t.token_type = token.get('token_type')
    t.access_token = token.get('access_token')
    t.refresh_token = token.get('refresh_token')
    t.expires_at = token.get('expires_at')
    t.user = u

    t.save()

    # send the user back where they were going
    # (or home, since the 'next' URL was not set up)
    return redirect('dashboard:home')
