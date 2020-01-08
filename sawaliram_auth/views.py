"""Define the View classes that handle auth requests"""

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse

from sawaliram_auth.models import User, VolunteerRequest, Bookmark
from sawaliram_auth.forms import SignInForm, SignUpForm
from sawaliram_auth.decorators import volunteer_permission_required
from dashboard.models import Question, AnswerDraft


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

            login(request, user)
            return redirect(request.POST.get('next', 'public_website:home'))
        context = {
            'form': form
        }
        return render(request, 'sawaliram_auth/signup.html', context)


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
                login(request, user)
                return redirect(request.POST.get('next', 'public_website:home'))
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
        draft_to_remove = AnswerDraft.objects.get(id=request.POST.get('draft-id'))
        draft_to_remove.delete()
        messages.success(request, 'Draft has been deleted!')
        return redirect('public_website:user-profile', user_id=request.user.id)
