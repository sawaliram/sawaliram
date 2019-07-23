"""Define the View classes that handle auth requests"""

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from sawaliram_auth.models import User, VolunteerRequest
from sawaliram_auth.forms import SignInForm, SignUpForm


class SignupView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
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
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()

            users = Group.objects.get(name='users')
            users.user_set.add(user)

            login(request, user)
            return redirect(request.POST.get('next', 'dashboard:home'))
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
        volunteer_request = VolunteerRequest(
            expert='expert' in request.POST.getlist('volunteer-request'),
            writer='writer' in request.POST.getlist('volunteer-request'),
            translator='translator' in request.POST.getlist('volunteer-request'),
            expert_application=request.POST['expert-entry-submission'],
            writer_application=request.POST['writer-entry-submission'],
            translator_application=request.POST['translator-entry-submission'],
            user=request.user
        )
        volunteer_request.save()

        volunteers = Group.objects.get(name='volunteers')
        volunteers.user_set.add(request.user)

        return redirect('dashboard:home')


class SigninView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
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
                return redirect(request.POST.get('next', 'dashboard:home'))
            else:
                context = {
                    'form': form,
                    'validation_error': True
                }
                return render(request, 'sawaliram_auth/signin.html', context)


class SignoutView(View):

    def get(self, request):
        logout(request)
        return redirect('dashboard:home')
