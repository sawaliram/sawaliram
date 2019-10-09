"""Define the View classes that will handle the public website pages"""

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password, make_password
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from django.core.paginator import Paginator

from dashboard.models import AnswerDraft, Dataset, Answer, Question
from sawaliram_auth.models import User, Bookmark
# from dashboard.views import ViewQuestionsView

import random
import urllib
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


class SearchView(View):
    def get_queryset(self, request):
        if 'q' in request.GET:
            return Question.objects \
                    .filter(
                        Q(question_text__icontains=request.GET.get('q')) |
                        Q(question_text_english__icontains=request.GET.get('q')) |
                        Q(school__icontains=request.GET.get('q')) |
                        Q(area__icontains=request.GET.get('q')) |
                        Q(state__icontains=request.GET.get('q')) |
                        Q(field_of_interest__icontains=request.GET.get('q'))
                    )
        else:
            return Question.objects.all()

    def get_template(self, request):
        '''
        Returns the template to render at the end (can be overridden
        by subclasses
        '''
        return 'public_website/search.html'

    def get_page_title(self, request):
        """
        Returns the page title for  breadcrumbs and <title> tag
        """
        return 'Search'

    def get_enable_breadcrumbs(self, request):
        """
        Returns the setting to enable breadcrumbs
        """
        return 'No'

    def get_search_query(self, request):
        """
        Returns the search query
        """
        if 'q' in request.GET:
            return request.GET.get('q')
        else:
            return ""

    def get(self, request):

        # load page from session if arriving from Submit Answer/Review Answer
        if '/answer/new' in str(request.META.get('HTTP_REFERER')):
            if 'answer_questions_url' in request.session:
                redirect_url = request.session['answer_questions_url']
                del request.session['answer_questions_url']
                return redirect(redirect_url)
        elif '/review' in str(request.META.get('HTTP_REFERER')):
            if 'review_answers_url' in request.session:
                redirect_url = request.session['review_answers_url']
                del request.session['review_answers_url']
                return redirect(redirect_url)

        result = self.get_queryset(request)

        # get values for filter
        subjects = [
            'Chemistry',
            'Biology',
            'Physics',
            'Mathematics',
            'Arts & Recreation',
            'Earth & Environment',
            'History, Philosophy & Practice of Science',
            'Humans & Society',
            'Language & Literature',
            'Technology & Applied Science',
        ]

        available_subjects = list(result.order_by()
                                        .values_list('field_of_interest', flat=True)
                                        .distinct('field_of_interest')
                                        .values_list('field_of_interest'))
        # convert list of tuples to list of strings
        available_subjects = [''.join(item) for item in available_subjects]

        states = result.order_by() \
                       .values_list('state') \
                       .distinct('state') \
                       .values('state')

        curriculums = result.order_by() \
                            .values_list('curriculum_followed') \
                            .distinct('curriculum_followed') \
                            .values('curriculum_followed')

        languages = result.order_by() \
                          .values_list('question_language') \
                          .distinct('question_language') \
                          .values('question_language')

        # apply filters if any
        subjects_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('subject')]
        if subjects_to_filter_by:
            result = result.filter(field_of_interest__in=subjects_to_filter_by)

        states_to_filter_by = request.GET.getlist('state')
        if states_to_filter_by:
            result = result.filter(state__in=states_to_filter_by)

        curriculums_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('curriculum')]
        if curriculums_to_filter_by:
            result = result.filter(curriculum_followed__in=curriculums_to_filter_by)

        languages_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('language')]
        if languages_to_filter_by:
            result = result.filter(question_language__in=languages_to_filter_by)

        # sort the results if sort-by parameter exists
        # default: newest
        sort_by = request.GET.get('sort-by', 'newest')

        if sort_by == 'newest':
            result = result.order_by('-created_on')

        # save list of IDs for Submit Answer/Review Answer
        page_title = self.get_page_title(request)
        if page_title == 'Review Answers' or page_title == 'Answer Questions':
            result_id_list = [id['id'] for id in result.values('id')]
            request.session['result_id_list'] = result_id_list

        paginator = Paginator(result, 15)

        page = request.GET.get('page', 1)
        result_page_one = paginator.get_page(page)

        # get list of IDs of bookmarked items
        bookmark_id_list = Bookmark.objects.filter(user_id=request.user.id) \
                                           .values_list('question_id') \
                                           .values('question_id')
        bookmarks = [bookmark['question_id'] for bookmark in bookmark_id_list]

        context = {
            'grey_background': 'True',
            'page_title': page_title,
            'enable_breadcrumbs': self.get_enable_breadcrumbs(request),
            'results': result_page_one,
            'result_size': result.count(),
            'subjects': subjects,
            'available_subjects': available_subjects,
            'states': states,
            'curriculums': curriculums,
            'languages': languages,
            'subjects_to_filter_by': subjects_to_filter_by,
            'states_to_filter_by': states_to_filter_by,
            'curriculums_to_filter_by': curriculums_to_filter_by,
            'languages_to_filter_by': languages_to_filter_by,
            'bookmarks': bookmarks,
            'search_query': self.get_search_query(request),
            'sort_by': sort_by
        }
        return render(request, self.get_template(request), context)


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
