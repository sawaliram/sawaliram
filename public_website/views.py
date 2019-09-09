"""Define the View classes that will handle the public website pages"""

from django.shortcuts import render
from django.views import View
from django.urls.base import resolve

from sawaliram_auth.models import ProfileSettings
from dashboard.models import AnswerDraft, Dataset, Answer

from pprint import pprint


class HomeView(View):
    def get(self, request):
        context = {
            'dashboard': 'False',
            'page_title': 'Home'
        }
        return render(request, 'public_website/home.html', context)


class UserProfileView(View):
    def get(self, request, user_id):
        selected_user = ProfileSettings.objects.select_related('user_id').get(user_id=user_id)
        answer_drafts = AnswerDraft.objects.filter(answered_by_id=user_id)
        submitted_questions = Dataset.objects.filter(submitted_by=user_id)
        submitted_answers = Answer.objects.filter(answered_by=user_id)
        bookmarked_questions = request.user.bookmarks.filter(content_type='question')
        bookmarked_articles = request.user.bookmarks.filter(content_type='article')
        context = {
            'dashboard': 'False',
            'page_title': selected_user.user_id.first_name + "'s Profile",
            'selected_user': selected_user,
            'answer_drafts': answer_drafts,
            'submitted_questions': submitted_questions,
            'submitted_answers': submitted_answers,
            'bookmarked_questions': bookmarked_questions,
            'bookmarked_articles': bookmarked_articles,
        }
        return render(request, 'public_website/user-profile.html', context)
