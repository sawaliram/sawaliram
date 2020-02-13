"""Define the View classes that handle auth requests"""

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


def send_verification_email(user):

    salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
    verification_code = hashlib.sha1((salt + user.get_full_name()).encode('utf-8')).hexdigest()

    profile, created = Profile.objects.get_or_create(user=user)
    profile.verification_code = verification_code
    profile.verification_code_expiry = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=3), "%Y-%m-%d %H:%M:%S")
    profile.save()

    message = 'Hello ' + user.first_name + ',<br>'
    message += 'Thank you for signing up with Sawaliram! Please click on this link: https://sawaliram.org/users/verify/' + verification_code + ' to verify your email. <br><br>Yours truly,<br>Sawaliram'

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
            'form': form
        }
        return render(request, 'sawaliram_auth/signup.html', context)

    def post(self, request):
        form = SignUpForm(request.POST, auto_id=False)
        if form.is_valid():
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

            send_verification_email(user)

            context = {
                'message': 'Thank you for joining Sawaliram! A verification mail will be sent to your registered email address. Make sure to check the spam folder if you do not receive the email shortly.',
                'show_resend': True,
                'resend_message': "Did not receive the verification mail?",
                'user_id': user.id
            }
            return render(request, 'sawaliram_auth/verify-email-info.html', context)
        context = {
            'form': form
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
class HowCanIHelpView(View):

    def get(self, request):
        if request.user.groups.filter(name='volunteers').exists():
            return redirect('dashboard:home')
        return render(request, 'sawaliram_auth/how-can-i-help.html')

    def post(self, request):

        volunteer_requests = request.POST.getlist('volunteer-request')
        for volunteer_request in volunteer_requests:
            new_volunteer_request = VolunteerRequest(
                permission_requested=volunteer_request + 's',
                request_text=request.POST[volunteer_request+'-entry-submission'],
                status='pending',
                requested_by=request.user
            )
            new_volunteer_request.save()

        volunteers = Group.objects.get(name='volunteers')
        volunteers.user_set.add(request.user)

        return redirect('dashboard:home')


class SigninView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('public_website:home')
        form = SignInForm(auto_id=False)
        context = {
            'form': form
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
class ManageUsersView(View):

    def get(self, request):

        users = User.objects.values()

        # add groups to users
        for user in users:
            user['groups'] = User.objects.get(id=user['id']).groups.values_list('name', flat=True)

        pending_requests = VolunteerRequest.objects.filter(status='pending')

        context = {
            'users': users,
            'pending_requests': pending_requests,
            'page_title': 'Manage Users',
            'enable_breadcrumbs': 'Yes',
            'grey_background': 'True'
        }

        return render(request, 'sawaliram_auth/manage-users.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class UpdateUserPermissions(View):

    def post(self, request):
        granted_permissions = request.POST.getlist('granted-permissions')
        permissions = ['admins', 'experts', 'writers', 'translators']
        user = User.objects.get(id=request.POST.get('user-id'))

        for permission in permissions:
            if permission in granted_permissions:
                Group.objects.get(name=permission).user_set.add(user)
                # remove pending volunteer request, if any
                pending_requests = VolunteerRequest.objects \
                                                   .filter(requested_by_id=user.id) \
                                                   .filter(permission_requested=permission) \
                                                   .filter(status='pending')
                if pending_requests:
                    for pending_request in pending_requests:
                        pending_request.status = 'processed'
                        pending_request.save()
            else:
                pass
                Group.objects.get(name=permission).user_set.remove(user)

        messages.success(request, 'User permissions updated for ' + user.first_name + ' ' + user.last_name)
        return redirect('sawaliram_auth:manage-users')


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class GrantOrDenyUserPermission(View):

    def post(self, request):
        group = Group.objects.get(name=request.POST.get('permission'))
        permission_action = request.POST.get('permission-action')
        user = User.objects.get(id=request.POST.get('user-id'))

        if permission_action == 'grant':
            group.user_set.add(user)

        request_entry = VolunteerRequest.objects.get(id=request.POST.get('request-id'))
        request_entry.status = 'processed'
        request_entry.save()

        messages.success(request, user.first_name + ' ' + user.last_name + ' was granted ' + request.POST.get('permission') + ' access')
        return redirect('sawaliram_auth:manage-users')


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
        messages.success(request, 'Bookmark has been deleted!')
        return redirect('public_website:user-profile', user_id=request.user.id)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class RemoveDraft(View):
    def post(self, request):
        draft_to_remove = Answer.objects.get(id=request.POST.get('draft-id'))
        draft_to_remove.delete()
        messages.success(request, 'Draft has been deleted!')
        return redirect('public_website:user-profile', user_id=request.user.id)
