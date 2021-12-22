"""Define the View classes that handle auth requests"""

from django.utils.translation import gettext as _

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from sawaliram_auth.models import User, VolunteerRequest, Bookmark, Profile
from sawaliram_auth.forms import (
    SignInForm,
    SignUpForm,
    ResetPasswordForm,
    ChangePasswordForm)
from sawaliram_auth.decorators import volunteer_permission_required
from dashboard.models import Question, Answer

from pprint import pprint
import hashlib
import random
import datetime
import requests

def send_verification_email(user):

    salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
    verification_code = hashlib.sha1((salt + user.get_full_name()).encode('utf-8')).hexdigest()

    profile, profile_created = Profile.objects.get_or_create(user=user)
    profile.verification_code = verification_code
    profile.verification_code_expiry = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=3), "%Y-%m-%d %H:%M:%S")
    if profile_created:
        profile.profile_picture = '/static/user/default.png'
        profile_bg_colors = [
            '#7dc190', '#f4f7db', '#46a1a2', '#618df0', '#7dc190', '#0086ff', '#ffdc00', '#de4d53', '#a2d9e8', '#5cf892', '#a15ddd', '#81d62d', '#ff4c2a', '#3680b7', '#ffa300', '#9bf1f0', '#dfbbd8', '#ffdab6', '#61ff9a', '#74cefd'
        ]
        profile.profile_picture_bg = random.choice(profile_bg_colors)
    profile.save()

    message = 'Hello ' + user.first_name + ',<br>'
    message += 'Thank you for signing up with Sawaliram! Please click on this link: https://sawaliram.org/users/verify/' + verification_code + ' to verify your email. <br><br>Yours truly,<br>Sawaliram'

    if not settings.DEBUG:

        send_mail(
            subject='Sawaliram - verify your email',
            message='',
            html_message=message,
            from_email='"Sawaliram" <mail@sawaliram.org>',
            recipient_list=[user.email],
            fail_silently=False,
        )


class SignupView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('public_website:home')
        form = SignUpForm(auto_id=False)
        context = {
            'form': form,
            'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY
        }
        return render(request, 'sawaliram_auth/signup.html', context)

    def post(self, request):
        form = SignUpForm(request.POST, auto_id=False)


        if form.is_valid():

            captcha_token = request.POST.get("g-recaptcha-response")
            cap_url = "https://www.google.com/recaptcha/api/siteverify"
            cap_secret = settings.GOOGLE_RECAPTCHA_SECRET_KEY

            cap_data = {"secret":cap_secret,"response":captcha_token}

            cap_server_response = requests.post(url=cap_url,data=cap_data)
            cap_json = cap_server_response.json()
            print(cap_json)

            if cap_json['success']:

                user = User.objects.create_user(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    organisation=form.cleaned_data['organisation'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                user.save()

                users = Group.objects.get(name='users')
                users.user_set.add(user)
               
                if not settings.DEBUG:

                    send_verification_email(user)

                    context = {
                        'message': 'Thank you for joining Sawaliram! A verification mail will be sent to your registered email address. Make sure to check the spam folder if you do not receive the email shortly.',
                        'show_resend': True,
                        'resend_message': "Did not receive the verification mail?",
                        'user_id': user.id
                    }
                    return render(request, 'sawaliram_auth/verify-email-info.html', context)
                else:
                    form = SignInForm(auto_id=False)
                    context = {
                        'form': form,
                        
                    }
                    test_mail={'Subject':'Sawaliram - verify your email',
                         'From':'mail@sawaliram.org',
                          'To': user.email,
                          'Message':'Hello ' + user.first_name + ' Thank you for signing up with Sawaliram!'
                         }
                    print(test_mail)

                    return render(request, 'sawaliram_auth/signin.html', context)

            else:
                context = {
                    'form': form,
                    'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY
                }
                messages.error(request, _('Error! Invalid Captcha!.'))
                return render(request, 'sawaliram_auth/signup.html', context)

        context = {
            'form': form,
            'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY
        }
        return render(request, 'sawaliram_auth/signup.html', context)


class VerifyEmailMessagesView(View):

    def get(self, request, message, show_resend=True):
        context = {
            'message': message,
            'show_resend': show_resend
        }
        return render(request, 'sawaliram_auth/verify-email-info.html', context)

    def post(self, request):
        user = User.objects.get(pk=request.POST.get('user-id'))
        send_verification_email(user)

        context = {
            'message': 'A verification mail will be sent to your registered email address. Make sure to check the spam folder if you do not receive the email shortly.',
            'show_resend': False
        }
        return render(request, 'sawaliram_auth/verify-email-info.html', context)


class VerifyEmailView(View):

    def get(self, request, verification_code):

        try:
            user_profile = Profile.objects.get(verification_code=verification_code)
            if timezone.now() > user_profile.verification_code_expiry:
                context = {
                    'message': "This verification mail expired! Click the 'Resend Mail' button to generate a new verification mail.",
                    'show_resend': True,
                    'resend_message': '',
                    'user_id': user_profile.user.id
                }
                return render(request, 'sawaliram_auth/verify-email-info.html', context)
            else:
                user_profile.email_verified = True
                user_profile.save()
                return render(request, 'sawaliram_auth/verify-email-success.html')
        except Profile.DoesNotExist:
            context = {
                'message': "Something's wrong with the verification link. Make sure the link from the verification mail is correctly copied into the address bar. If the problem persists, please <a href=\"\\users\\signin\">sign-in</a> and generate a new verification mail",
                'show_resend': False
            }
            return render(request, 'sawaliram_auth/verify-email-info.html', context)


@method_decorator(login_required, name='dispatch')
class RequestAccess(View):

    def get(self, request):
        return render(request, 'sawaliram_auth/request-access.html')

    def post(self, request):

        permissions_requested = []
        if request.POST.get('expert-permission') == 'true':
            permissions_requested.append('E')
        if request.POST.get('writer-permission') == 'true':
            permissions_requested.append('W')
        if request.POST.get('translator-permission') == 'true':
            permissions_requested.append('T')

        if request.POST.get('permission-writeup'):
            new_volunteer_request = VolunteerRequest(
                permissions_requested=''.join(permissions_requested),
                request_text=request.POST.get('permission-writeup'),
                status='pending',
                requested_by=request.user
            )
            new_volunteer_request.save()

        if request.user.groups.filter(name='volunteers').exists():
            messages.success(request, 'Your access request has been submitted!')
            return redirect('public_website:user-profile', user_id=request.user.id, active_tab='settings')
        else:
            volunteers = Group.objects.get(name='volunteers')
            volunteers.user_set.add(request.user)
            return redirect('dashboard:home')


class SigninView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('public_website:home')
        form = SignInForm(auto_id=False)
        context = {
            'form': form,
            
        }
        return render(request, 'sawaliram_auth/signin.html', context)

    def post(self, request):
        form = SignInForm(request.POST, auto_id=False)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'])
            if user is not None:
                if not settings.DEBUG:
                    try:
                        user_profile = Profile.objects.get(user=user.id)
                        if not user_profile.email_verified:
                            context = {
                                'message': 'Verify your registered email address to login to your Sawaliram account. Make sure to check your spam folder if you did not receive the email.',
                                'show_resend': True,
                                'resend_message': "Did not receive the verification mail?",
                                'user_id': user.id
                            }
                            return render(request, 'sawaliram_auth/verify-email-info.html', context)
                        else:
                            login(request, user)
                            if request.POST.get('next') != '':
                                return redirect(request.POST.get('next'))
                            else:
                                return redirect('public_website:home')
                    except Profile.DoesNotExist:
                        send_verification_email(user)
                        context = {
                            'message': 'Verify your registered email address to login to your Sawaliram account. Make sure to check your spam folder if you did not receive the email.',
                            'show_resend': True,
                            'resend_message': "Did not receive the verification mail?",
                            'user_id': user.id
                        }
                        return render(request, 'sawaliram_auth/verify-email-info.html', context)
                else:
                    login(request, user)
                    if request.POST.get('next') != '':
                        return redirect(request.POST.get('next'))
                    else:
                        return redirect('public_website:home')
            else:
                context = {
                    'form': form,
                    'validation_error': True
                }
                return render(request, 'sawaliram_auth/signin.html', context)
        else:
            context = {
                'form': form,
                'validation_error': True
            }
            return render(request, 'sawaliram_auth/signin.html', context)


class SignoutView(View):

    def get(self, request):
        logout(request)
        return redirect('public_website:home')


class ResetPasswordView(View):

    def get(self, request):
        form = ResetPasswordForm(auto_id=False)
        context = {
            'form': form
        }
        return render(request, 'sawaliram_auth/reset-password.html', context)

    def post(self, request):
        form = ResetPasswordForm(request.POST, auto_id=False)
        if form.is_valid():
            user = User.objects.get(email=request.POST.get('email'))
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            password_reset_code = hashlib.sha1((salt + user.email).encode('utf-8')).hexdigest()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.password_reset_code = password_reset_code
            profile.password_reset_code_expiry = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=3), "%Y-%m-%d %H:%M:%S")
            profile.save()

            message = 'Hello ' + user.first_name + ',<br>'
            message += 'Please click on this link: https://sawaliram.org/users/change-password-form/' + password_reset_code + ' to reset your password. <br><br>Yours truly,<br>Sawaliram'

            send_mail(
                subject='Sawaliram - reset your password',
                message='',
                html_message=message,
                from_email='"Sawaliram" <mail@sawaliram.org>',
                recipient_list=[user.email],
                fail_silently=False,
            )

            return render(request, 'sawaliram_auth/reset-password-sent.html')
        else:
            context = {
                'form': form
            }
            return render(request, 'sawaliram_auth/reset-password.html', context)


class ChangePasswordFormView(View):

    def get(self, request, password_reset_code):
        try:
            user_profile = Profile.objects.get(password_reset_code=password_reset_code)
            if timezone.now() > user_profile.password_reset_code_expiry:
                context = {
                    'message': "This password reset link has expired! Click <a href=\"\\users\\reset-password\">here</a> to generate a new link.",
                    'success': False
                }
                return render(request, 'sawaliram_auth/change-password-info.html', context)
            else:
                form = ChangePasswordForm(auto_id=False)
                context = {
                    'form': form,
                    'user_id': user_profile.user.id
                }
                return render(request, 'sawaliram_auth/change-password.html', context)
        except Profile.DoesNotExist:
            context = {
                'message': "Something's wrong with the password reset link. Make sure the link from the mail is correctly copied into the address bar. If the problem persists, please click <a href=\"\\users\\reset-password\">here</a> and generate a new verification mail.",
                'success': False
            }
            return render(request, 'sawaliram_auth/change-password-info.html', context)


class ChangePasswordView(View):

    def post(self, request):
        form = ChangePasswordForm(request.POST, auto_id=False)
        if form.is_valid():
            user = User.objects.get(pk=request.POST.get('user'))
            user.set_password(request.POST.get('confirm_new_password'))
            user.save()
            return render(request, 'sawaliram_auth/change-password-success.html')
        else:
            context = {
                'form': form,
                'user_id': request.POST.get('user')
            }
            return render(request, 'sawaliram_auth/change-password.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class GrantOrDenyUserPermission(View):

    def post(self, request):
        permissions = request.POST.getlist('permissions')
        permission_action = request.POST.get('permission-action')
        user = User.objects.get(id=request.POST.get('user-id'))

        display_permissions = []
        for permission in permissions:
            display_permissions.append(permission[:-1].title())

        if permission_action == 'grant':
            for permission in permissions:
                group = Group.objects.get(name=permission)
                group.user_set.add(user)
            messages.success(request, (_(user.first_name + ' ' + user.last_name + ' was granted following access: ' + ', '.join(display_permissions))))
        elif permission_action == 'deny':
            messages.success(request, (_(user.first_name + ' ' + user.last_name + ' was denied following access: ' + ', '.join(display_permissions))))

        request_entry = VolunteerRequest.objects.get(id=request.POST.get('request-id'))
        request_entry.status = 'processed'
        request_entry.save()

        request.session['active_tab'] = 'access_requests'

        return redirect(request.META['HTTP_REFERER'])


@method_decorator(csrf_exempt, name='dispatch')
class AddBookmark(View):
    def post(self, request):
        new_bookmark = Bookmark(
            content_type=request.POST.get('content'),
            question=Question.objects.get(id=request.POST.get('id')),
            user=request.user
        )
        new_bookmark.save()

        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class RemoveBookmark(View):
    def post(self, request):
        bookmark_to_remove = Bookmark.objects.get(
            content_type=request.POST.get('content'),
            question=request.POST.get('id'))
        bookmark_to_remove.delete()

        return HttpResponse()


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class DeleteBookmark(View):
    def post(self, request):
        bookmark_to_remove = Bookmark.objects.get(
            content_type=request.POST.get('content-type'),
            question=request.POST.get('question-id'))
        bookmark_to_remove.delete()
        messages.success(request, (_('Bookmark has been deleted!')))
        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='bookmarks')


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class RemoveDraft(View):
    def post(self, request):
        draft_to_remove = Answer.objects.get(id=request.POST.get('draft-id'))
        draft_to_remove.delete()
        messages.success(request, (_('The draft answer has been deleted!')))
        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='drafts')
