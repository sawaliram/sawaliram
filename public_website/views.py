"""Define the View classes that will handle the public website pages"""

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password, make_password
from django.http import Http404

from dashboard.models import AnswerDraft, Dataset, Answer
from sawaliram_auth.models import User

import random
from pprint import pprint


class HomeView(View):
    def get(self, request):
        banner_texts_list = [
            'Leaves or Fruits or Sprouting Shoots?',
            'Sun or Stars or Life on Mars?',
            'Constellations or the fate of nations?',
            'Curly tresses or yellow school buses?'
        ]
        context = {
            'dashboard': 'False',
            'page_title': 'Home',
            'first_banner_text': random.choice(banner_texts_list)
        }
        return render(request, 'public_website/home.html', context)


class UserProfileView(View):
    def get(self, request, user_id):

        if not User.objects.filter(id=user_id).exists():
            raise Http404
        else:
            selected_user = User.objects.get(id=user_id)
            answer_drafts = AnswerDraft.objects.filter(answered_by_id=user_id)
            submitted_questions = Dataset.objects.filter(submitted_by=user_id)
            submitted_answers = Answer.objects.filter(answered_by=user_id)
            bookmarked_questions = selected_user.bookmarks.filter(content_type='question')
            bookmarked_articles = selected_user.bookmarks.filter(content_type='article')
            context = {
                'dashboard': 'False',
                'page_title': selected_user.first_name + "'s Profile",
                'enable_breadcrumbs': 'Yes',
                'selected_user': selected_user,
                'answer_drafts': answer_drafts,
                'submitted_questions': submitted_questions,
                'submitted_answers': submitted_answers,
                'bookmarked_questions': bookmarked_questions,
                'bookmarked_articles': bookmarked_articles,
            }
            return render(request, 'public_website/user-profile.html', context)

    def post(self, request, user_id):
        user = User.objects.get(id=request.user.id)
        if request.POST.get('organisation-name'):
            user.organisation = request.POST.get('organisation-name')
            user.save()
            if request.POST.get('organisation-role'):
                user.organisation_role = request.POST.get('organisation-role')
                user.save()
            messages.success(request, ('Your organisation details have been updated!'))
        elif request.POST.get('current-password'):
            match_check_old = check_password(request.POST.get('current-password'), request.user.password)
            if match_check_old:
                if request.POST.get('new-password') == request.POST.get('confirm-new-password'):
                    match_check_new = check_password(request.POST.get('new-password'), request.user.password)
                    if match_check_new:
                        messages.error(request, ('New password cannot be same as the current password'))
                    else:
                        user.password = make_password(password=request.POST.get('new-password'))
                        user.save()
                        login(request, user)
                        messages.success(request, ('Your password has been updated!'))
                else:
                    messages.error(request, ('Make sure you entered the new password correctly both times'))
            else:
                messages.error(request, ('The password you entered is incorrect'))

        return redirect('public_website:user-profile', user_id=request.user.id)


class GetInvolvedView(View):
    def get(self, request):
        context = {
            'page_title': 'Get Involved',
        }
        return render(request, 'public_website/get-involved.html', context)
