"""Define the View classes that will handle the public website pages"""

import warnings

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.views import View
from django.utils.translation import gettext as _
from django.utils.translation import (
    ngettext,
    pgettext,
)
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password, make_password
from django.http import Http404, JsonResponse
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.mail import send_mail

from django.conf import settings
from public_website.forms import ContactPageForm
from django.views.generic import FormView
from django.urls import reverse

from dashboard.models import (
    Dataset,
    Answer,
    Question,
    Article,
    PublishedArticle,
    ArticleDraft,
    SubmittedArticle,
    ArticleTranslation,
    DraftAnswerTranslation,
    DraftArticleTranslation,
    SubmittedArticleTranslation,
    SubmittedAnswerTranslation,
    PublishedArticleTranslation,
    PublishedAnswerTranslation,
    AnswerTranslation,
    AnswerTranslationCredit,
    ArticleTranslationCredit,
)
from sawaliram_auth.models import User, Bookmark, Notification
from public_website.models import AnswerUserComment, ContactUsSubmission

import re
import random
import urllib
from pprint import pprint
import json
import requests
import collections
from .lang import *
from django.db.models import Count
import datetime
from datetime import timedelta
from datetime import datetime as ts
import os
import time
import csv



class HomeView(View):
    def get(self, request):
        banner_texts_list = [
            _('Leaves or fruits or sprouting shoots?'),
            _('Sun or stars or life on Mars?'),
            _('Constellations or the fate of nations?'),
            _('Curly tresses or yellow school buses?'),
            _('Birds in the sky or a firefly?'),
        ]
        context = {
            'dashboard': 'False',
            'page_title': pgettext('website homepage', 'Home'),
            'first_banner_text': random.choice(banner_texts_list)
        }
        return render(request, 'public_website/home.html', context)


class SetLanguageView(View):
    def post(self, request, language):
        request.session['lang'] = language

        response = redirect(request.POST.get('next')
            or request.GET.get('next')
            or 'public_website:home')
        response.set_cookie('lang', language)

        return response

    def get(self, request, language):
        # TODO: display language picker or something
        # it's bad practice to set params on a GET request
        # or maybe it doesn't matter in this case?
        return self.post(request, language)


class SearchView(View):

    filters = {
        'search_categories': [],
        'question_categories': [],
    }

    def set_filters(self, params):
        '''
        Process filters, setting default values if necessary
        '''

        search_categories = params.getlist('category')

        # Select only questions by default, if no category selected
        if not search_categories:
            search_categories.append('questions')


        question_categories = []
        if 'questions' in params:
            question_categories = params.getlist('questions')

        # TODO: add other filters here too

        filters = {
            'search_categories': search_categories,
            'question_categories': question_categories,
        }

        self.filters = filters
        return filters

    def get_querysets(self, request):
        '''
        Returns a dict of querysets, one for each data type
        '''

        results = {}

        # Backwards-compatibility for the old 'get_queryset' function
        if hasattr(self, 'get_queryset'):
            warnings.warn('get_queryset is deprecated. Please use get_querysets instead.')

            results['questions'] = self.get_queryset(request)
            return results

        filters = self.filters
        search_categories = filters.get('search_categories', [])

        # Select only questions by default, if no category selected
        if not search_categories:
            search_categories.append('questions')


        if 'q' in request.GET and request.GET.get('q') != '':
            if not search_categories:
                results['questions'] = Question.objects.filter(
                            Q(pk__iexact=request.GET.get('q')) |
                            Q(question_text__search=request.GET.get('q')) |
                            Q(question_text_english__search=request.GET.get('q')) |
                            Q(school__search=request.GET.get('q')) |
                            Q(area__search=request.GET.get('q')) |
                            Q(state__search=request.GET.get('q')) |
                            Q(field_of_interest__search=request.GET.get('q')) |
                            Q(published_source__search=request.GET.get('q'))
                        )
                results['articles'] = PublishedArticle.objects.filter(
                            Q(title__search=request.GET.get('q')) |
                            Q(pk__iexact=request.GET.get('q')) |
                            Q(body__search=request.GET.get('q'))
                        ).order_by('-updated_on')
            else:
                if 'questions' in search_categories:
                    results['questions'] = Question.objects.filter(
                            Q(pk__iexact=request.GET.get('q')) |
                            Q(question_text__search=request.GET.get('q')) |
                            Q(question_text_english__search=request.GET.get('q')) |
                            Q(school__search=request.GET.get('q')) |
                            Q(area__search=request.GET.get('q')) |
                            Q(state__search=request.GET.get('q')) |
                            Q(field_of_interest__search=request.GET.get('q')) |
                            Q(published_source__search=request.GET.get('q'))
                        )
                else:
                    results['questions'] = Question.objects.none()

                if 'articles' in search_categories:
                    results['articles'] = PublishedArticle.objects.filter(
                            Q(title__search=request.GET.get('q')) |
                            Q(pk__iexact=request.GET.get('q')) |
                            Q(body__search=request.GET.get('q'))
                        ).order_by('-updated_on')
                else:
                    results['articles'] = PublishedArticle.objects.none()
        else:
            if 'questions' in search_categories:
                results['questions'] = Question.objects.all()
            else:
                results['questions'] = Question.objects.none()

            if 'articles' in search_categories:
                results['articles'] = PublishedArticle.objects.all()
            else:
                results['articles'] = PublishedArticle.objects.none()

        return results

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
        return _('Search')

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

        # load filters
        filters = self.set_filters(request.GET)

        results = self.get_querysets(request)

        questions = results.get('questions') or Question.objects.none()
        articles = results.get('articles') or Article.objects.none()

        # get values for filter
        subjects = [
            'Biology',
            'Chemistry',
            'Physics',
            'Mathematics',
            'Earth & Environment',
            'History, Philosophy & Practice of Science',
            'Technology & Applied Science',
            'Humans & Society',
            'Geography & History',
            'Language & Literature',
            'Arts & Recreation',
        ]

        # TODO: Generalise the category filter
        question_categories = self.filters.get('question_categories', [])
        if len(question_categories) != 0:
            questions_queryset = []

            if 'answered' in question_categories:
                answered_questions = questions.filter(answers__status='published')
                questions_queryset = answered_questions

            if 'unanswered' in question_categories:
                unanswered_questions = questions.exclude(answers__status='published')

                if type(questions_queryset) is QuerySet:
                    questions_queryset = questions_queryset | unanswered_questions
                else:
                    questions_queryset = unanswered_questions

            questions = questions_queryset


        available_subjects = list(questions.order_by()
                                        .values_list('field_of_interest', flat=True)
                                        .distinct('field_of_interest')
                                        .values_list('field_of_interest'))

        # convert list of tuples to list of strings
        available_subjects = [''.join(item) for item in available_subjects]

        states = questions.order_by() \
            .values_list('state') \
            .distinct('state') \
            .values('state') \
            .exclude(state__exact='') \
            .exclude(state__isnull=True)

        curriculums = questions.order_by() \
                            .values_list('curriculum_followed') \
                            .distinct('curriculum_followed') \
                            .values('curriculum_followed') \
                            .exclude(curriculum_followed__exact='') \
                            .exclude(curriculum_followed__isnull=True)

        languages = questions.order_by() \
            .values_list('language') \
            .distinct('language') \
            .values('language') \
            .exclude(language__exact='') \
            .exclude(language__isnull=True)

        # apply filters if any
        subjects_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('subject')]
        if subjects_to_filter_by:
            questions = questions.filter(field_of_interest__in=subjects_to_filter_by)

        states_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('state')]
        if states_to_filter_by:
            questions = questions.filter(state__in=states_to_filter_by)

        curriculums_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('curriculum')]
        if curriculums_to_filter_by:
            questions = questions.filter(curriculum_followed__in=curriculums_to_filter_by)

        languages_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('language')]
        if languages_to_filter_by:
            questions = questions.filter(language__in=languages_to_filter_by)
            articles = articles.filter(language__in=languages_to_filter_by) # TODO support translations


        # sort the questions if sort-by parameter exists
        # default: newest and comments(for Review Answers page)
        page_title = self.get_page_title(request)
        if page_title == _('Review Answers'):
            sort_by = request.GET.get('sort-by', 'comments')
        else:
            sort_by = request.GET.get('sort-by', 'newest')


        if sort_by == 'newest':
            questions = questions.order_by('-created_on')
            articles = articles.order_by('-published_on')
        if sort_by == 'oldest':
            questions = questions.order_by('created_on')
            articles = articles.order_by('published_on')
        if sort_by == 'comments':
            questions = questions
            articles = articles
        if sort_by == "date":
            questions = questions.order_by('published_date')
            articles = articles.order_by('published_on')

        # save list of IDs for Submit Answer/Review Answer
        if page_title == _('Review Answers') or page_title == _('Answer Questions'):
            result_id_list = [id['id'] for id in questions.values('id')]
            request.session['result_id_list'] = result_id_list
        

        ITEMS_PER_PAGE = 15

        paginator = Paginator(questions, ITEMS_PER_PAGE)
        page = request.GET.get('page', 1)


        # Adding the number of questions/articles being shown based on the page number
        start_index = (int(page)-1)*ITEMS_PER_PAGE + 1

        search_categories = self.filters.get('search_categories', [])

        if ('articles' in search_categories and not 'questions' in search_categories):
            if (start_index + ITEMS_PER_PAGE <=  articles.count()):
                end_index = start_index + ITEMS_PER_PAGE
            else:
                end_index = articles.count()
        else:
            if (start_index + ITEMS_PER_PAGE <= questions.count()):
                end_index = start_index + ITEMS_PER_PAGE
            else:
                end_index = questions.count() + articles.count()
        print(start_index, end_index)



        questions_page_one = paginator.get_page(page)

        # get list of IDs of bookmarked items
        bookmark_id_list = Bookmark.objects.filter(user_id=request.user.id) \
                                           .values_list('question_id') \
                                           .values('question_id')
        bookmarks = [bookmark['question_id'] for bookmark in bookmark_id_list]

        context = {
            'grey_background': 'True',
            'page_title': page_title,
            'enable_breadcrumbs': self.get_enable_breadcrumbs(request),
            'questions': questions_page_one,
            'result_size': questions.count(), 
            'start_index': start_index,
            'end_index': end_index,
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
            'sort_by': sort_by,
            'question_categories': question_categories
        }

        # only show articles on first page
        # TODO: make pagination smarter and inclusive
        # of all data types
        if articles and page == 1:
            context['articles'] = articles
            context['result_size'] = context['result_size'] + articles.count()

        # create list of active categories
        if page_title == _('Search') or page_title == _('Translate Content'):
            active_categories = request.GET.getlist('category')

            # Select questions only by default, if no category selected
            if not active_categories: active_categories.append('questions')
            context['active_categories'] = active_categories

            if request.GET.getlist('questions') and not active_categories:
                context['active_categories'].append('questions')

        return render(request, self.get_template(request), context)


class ViewAnswer(View):
    def get(self, request, question_id, answer_id):
        question = Question.objects.get(pk=question_id)
        answer = Answer.objects.get(pk=answer_id)

        # Set languages
        preferred_language = request.GET.get('lang')
        if preferred_language:
            question.set_language(preferred_language)
            answer.set_language(preferred_language)

        grey_background = 'True' if request.user.is_authenticated else 'False'

        context = {
            'dashboard': 'False',
            'page_title': _('View Answer'),
            'question': question,
            'answer': answer,
            'comments': answer.user_comments.all(),
        }

        return render(request, 'public_website/view-answer.html', context)


class ArticleView(View):
    def get(self, request, article, slug=None):
        article = get_object_or_404(Article, id=article)

        # Don't allow other people to see an unpublished draft
        if article.is_draft and article.author != request.user:
            raise Http404(_('Article does not exist'))

        # If it's under review, redirect to the review page
        if article.is_submitted:
            return redirect(
                'dashboard:review-article',
                article=article.id
            )

        # Set slug if required
        if slug != article.get_slug():
            return redirect('?'.join([
                reverse(
                    'public_website:view-article',
                    kwargs={
                        'slug': article.get_slug(),
                        'article': article.id,
                    }
                ),
                request.GET.urlencode(),
            ]))

        # Populate with language
        lang = request.GET.get('lang')
        if lang: article.set_language(lang)

        context = {
            'article': article,
            'page_title': 'View Article',
        }

        return render(request, 'public_website/view-article.html', context)


class SubmitUserCommentOnAnswer(View):
    def post(self, request, question_id, answer_id):
        """
        Save the submitted user comment to a particular answer
        """
        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            raise Http404(_('Answer does not exist'))

        comment = AnswerUserComment()
        comment.text = request.POST['comment-text']
        comment.answer = answer
        comment.author = request.user
        comment.save()

        # create notification
        if answer.submitted_by.id != request.user.id:
            answered_question = Question.objects.get(pk=question_id)
            if answered_question.language.lower() != 'en':
                question_text = answered_question.question_text_english
            else:
                question_text = answered_question.question_text

            comment_notification = Notification(
                notification_type='comment',
                title_text=_('%(name)s left a comment on your answer') % {
                    'name': str(request.user.get_full_name()),
                },
                description_text="On your answer for the question '" + question_text + "'.",
                target_url=reverse('public_website:view-answer', kwargs={'question_id': question_id, 'answer_id': answer_id}),
                user=answer.submitted_by
            )
            comment_notification.save()

        return redirect(
            'public_website:view-answer',
            question_id=question_id,
            answer_id=answer_id
        )


class DeleteUserCommentOnAnswer(View):
    def fetch_comment(self, question_id, answer_id, comment_id):
        """
        Return selected comment
        """

        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotexist:
            raise Http404(_('Answer does not exist'))

        try:
            comment = answer.user_comments.get(pk=comment_id)
        except AnswerUserComment.DoesNotExist:
            raise Http404(_('No matching comment'))

        return comment

    def get(self, request, question_id, answer_id, comment_id):
        """
        Confirm whether to delete a comment or not
        """

        comment = self.fetch_comment(question_id, answer_id, comment_id)

        context = {
            'comment': comment,
        }
        return render(request, 'dashboard/answers/delete_comment.html', context)

    def post(self, request, question_id, answer_id, comment_id):
        """
        Delete a previously published comment on an answer
        """

        comment = self.fetch_comment(question_id, answer_id, comment_id)

        if request.user != comment.author:
            raise PermissionDenied(_('You are not authorised to delete that comment.'))

        comment.delete()

        return redirect(
            'public_website:view-answer',
            question_id=question_id,
            answer_id=answer_id
        )


class UserProfileView(View):

    def get(self, request, user_id, active_tab='settings'):

        if not User.objects.filter(id=user_id).exists():
            raise Http404
        else:
            selected_user = User.objects.get(id=user_id)
            answer_drafts = Answer.objects.filter(submitted_by=user_id, status='draft')
            article_drafts = ArticleDraft.objects.filter(author=user_id)
            translated_answer_drafts = DraftAnswerTranslation.objects.filter(translated_by=user_id)
            translated_article_drafts = DraftArticleTranslation.objects.filter(translated_by=user_id)
            notifications = Notification.objects.filter(user=user_id).order_by('-created_on')
            submitted_questions = Dataset.objects.filter(submitted_by=user_id)
            submitted_answers = Answer.objects.filter(submitted_by=user_id, status='submitted')
            submitted_articles = SubmittedArticle.objects.filter(author=user_id)
            submitted_answer_translations = SubmittedAnswerTranslation.objects.filter(translated_by=user_id)
            submitted_article_translations = SubmittedArticleTranslation.objects.filter(translated_by=user_id)
            published_answers = Answer.objects.filter(submitted_by=user_id, status='published')
            published_articles = PublishedArticle.objects.filter(author=user_id)
            published_answer_translations = PublishedAnswerTranslation.objects.filter(translated_by=user_id)
            published_article_translations = PublishedArticleTranslation.objects.filter(translated_by=user_id)
            bookmarked_questions = selected_user.bookmarks.filter(content_type='question')
            bookmarked_articles = selected_user.bookmarks.filter(content_type='article')
            context = {
                'dashboard': 'False',
                # Translators: This is the title for the User Profile page
                'page_title': _("%(name)s's Profile") % {
                    'name': selected_user.first_name,
                },
                'selected_user': selected_user,
                'answer_drafts': answer_drafts,
                'article_drafts': article_drafts,
                'translated_answer_drafts': translated_answer_drafts,
                'translated_article_drafts': translated_article_drafts,
                'notifications': notifications,
                'submitted_questions': submitted_questions,
                'submitted_answers': submitted_answers,
                'submitted_articles': submitted_articles,
                'submitted_answer_translations': submitted_answer_translations,
                'submitted_article_translations': submitted_article_translations,
                'published_articles': published_articles,
                'published_answers': published_answers,
                'published_answer_translations': published_answer_translations,
                'published_article_translations': published_article_translations,
                'answers_count': len(submitted_answers) + len(published_answers),
                'translations_count': (
                    submitted_answer_translations.count() +
                    submitted_article_translations.count() +
                    published_answer_translations.count() +
                    published_article_translations.count()
                ),
                'bookmarked_questions': bookmarked_questions,
                'bookmarked_articles': bookmarked_articles,
                'active_tab': active_tab,
            }
            return render(request, 'public_website/user-profile.html', context)


class UpdateUserName(View):

    def post(self, request):
        request.user.first_name = request.POST.get('first-name')
        request.user.last_name = request.POST.get('last-name')
        request.user.save()

        messages.success(request, 'Your personal info has been updated.')
        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='settings')


class UpdateOrganisationInfo(View):

    def post(self, request):

        if request.POST.get('organisation-name'):
            request.user.organisation = request.POST.get('organisation-name')
            request.user.save()

        if request.POST.get('organisation-role'):
            request.user.organisation_role = request.POST.get('organisation-role')
            request.user.save()

        messages.success(request, 'Your organisation info has been updated.')
        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='settings')


class UpdateUserPassword(View):

    def post(self, request):

        check_old_password = check_password(request.POST.get('current-password'), request.user.password)
        if check_old_password:
            if request.POST.get('new-password') == request.POST.get('confirm-new-password'):
                match_check_new = check_password(request.POST.get('new-password'), request.user.password)
                if match_check_new:
                    messages.error(request, (_('New password cannot be same as the current password.')))
                else:
                    request.user.password = make_password(password=request.POST.get('new-password'))
                    request.user.save()
                    login(request, request.user)
                    messages.success(request, (_('Your password has been updated!')))
            else:
                messages.error(request, _('Make sure you entered the new password correctly both times.'))
        else:
            messages.error(request, _('The password you entered is incorrect.'))

        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='settings')


class UpdateProfilePicture(View):

    def post(self, request):
        user_profile = Profile.objects.get(user=request.user.id)
        user_profile.profile_picture = request.POST.get('picture')
        user_profile.save()

        messages.success(request, 'Your profile picture has been updated.')
        return redirect('public_website:user-profile', user_id=request.user.id)


class GetProfilePictureOptions(View):

    def get(self, request):
        img_src_list = []
        for count in range(1, 21):
            img_src_list.append('/static/user/default_profile_pictures/dpp_' + str(count) + '.png')
        context = {
            'current_picture_number': int(request.user.profile.profile_picture[-5:-4]),
            'img_src_list': img_src_list,
        }
        return HttpResponse(render_to_string('public_website/pick-profile-picture.html', context, request))


class ViewNotification(View):
    """
    Define the view to delete notification and redirect to target_url
    """
    def post(self, request):
        clicked_notification = Notification.objects.get(pk=request.POST.get('notification-id'))
        clicked_notification.delete()

        return redirect(request.POST.get('target-url'))


class GetInvolvedView(View):
    def get(self, request):
        context = {
            'page_title': _('Get Involved'),
        }
        return render(request, 'public_website/get-involved.html', context)


class About(View):
    def get(self, request):
        context = {
            'page_title': _('About'),
        }
        return render(request, 'public_website/about.html', context)


class ResearchPage(View):
    def get(self, request):
        context = {
            'page_title': _('Research')
        }
        return render(request, 'public_website/research.html', context)


class FAQPage(View):
    def get(self, request):
        context = {
            'page_title': _('Frequently Asked Questions')
        }
        return render(request, 'public_website/faq.html', context)


class ContactPage(FormView):
    def get(self, request):
        context = {
            'page_title': _('Contact Us'),
            'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY
        }
        return render(request, 'public_website/contact.html', context)

    template_name = 'public_website/contact.html'
    form_class = ContactPageForm

    def post(self, request):
        form = ContactPageForm(request.POST, auto_id=False)
        if form.is_valid():

            captcha_token = request.POST.get("g-recaptcha-response")
            cap_url = "https://www.google.com/recaptcha/api/siteverify"
            cap_secret = settings.GOOGLE_RECAPTCHA_SECRET_KEY

            cap_data = {"secret":cap_secret,"response":captcha_token}

            cap_server_response = requests.post(url=cap_url,data=cap_data)
            cap_json = cap_server_response.json()
            print(cap_json)

            if cap_json['success']:

                c = ContactUsSubmission()
                c.name = form.cleaned_data.get('fullname')
                c.emailid = form.cleaned_data.get('emailid')
                c.subject = form.cleaned_data.get('subject')
                c.message = form.cleaned_data.get('message')
                c.save()

                send_mail(
                    subject='[Contact] ' + form.cleaned_data.get('subject'),
                    message='',
                    html_message=form.cleaned_data.get('message') + '<br><br> Senders email: ' + form.cleaned_data.get('emailid'),
                    from_email='"Sawaliram" <mail@sawaliram.org>',
                    recipient_list=['mail.sawaliram@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, _('Your message has been sent! We will get back to you shortly.'))
                return redirect('public_website:contact')
            else:
                messages.error(request, _('Error! Invalid Captcha!.'))
                return redirect('public_website:contact')

        else:
            messages.error(request, _('Error! Message has not been submitted.'))
            return redirect('public_website:contact')


class ResourcesPage(View):

    def get(self, request):
        context = {
            'page_title': _('Resources')
        }
        return render(request, 'public_website/resources.html', context)


class ArticlesPage(View):

    def get(self, request):
        articles = PublishedArticle.objects.all()
        sort_by = request.GET.get('sort-by', 'newest')

        if sort_by == 'newest':
            articles = articles.order_by('-published_on')
        else:
            articles = articles.order_by('published_on')

        if len(articles) % 2 == 0:
            odd_article_count = 'False'
        else:
            odd_article_count = 'True'
        

        article_body= []


        for i in articles:
            ref = i.body
            fig_stripped = re.sub(r'\<figcaption\>.*?\<\/figcaption\>', '', ref)
            article_body.append(fig_stripped)
        

        context = {
            'page_title': _('Articles'),
            'articles': articles,
            'stripped_articles': article_body,
            'odd_article_count': odd_article_count,
            'sort_by': sort_by
        }
        return render(request, 'public_website/articles.html', context)


class AnalyticsPage(View):

    #Dictionary to hold {state_name:state_ISO_code}
    state_code = {'lakshadweep': 'LD', 'andaman and nicobar islands': 'AN', 'andaman & nicobar': 'AN', 'maharashtra': 'MH', 
                'andhra pradesh': 'AP', 'meghalaya': 'ML', 'arunachal pradesh': 'AR', 'manipur': 'MN', 'assam': 'AS', 
                'madhya pradesh': 'MP', 'bihar': 'BR', 'mizoram': 'MZ', 'chandigarh': 'CH', 'nagaland': 'NL', 
                'chhattisgarh': 'CT', 'odisha': 'OR', 'daman and diu': 'DD', 'punjab': 'PB', 'delhi': 'DL', 
                'puducherry': 'PY', 'dadra and nagar haveli': 'DN', 'rajasthan': 'RJ', 'goa': 'GA', 'sikkim': 'SK', 
                'gujarat': 'GJ', 'telangana': 'TG', 'himachal pradesh': 'HP', 'tamil nadu': 'TN', 'haryana': 'HR', 
                'tripura': 'TR', 'jharkhand': 'JH', 'uttar pradesh': 'UP', 'jammu and kashmir': 'JK', 'jammu & kashmir': 'JK', 'uttarakhand': 'UT', 
                'karnataka': 'KA', 'west bengal': 'WB', 'kerala': 'KL'}

    def get(self, request):
        """
        Returns the home page of analytics app.
        """
        # Translators: For all the language names in the database we need tranlation 
        # Each function getABC() returns the data for the ABC which is then added to context.

        year_labels, year_counts = self.getYearAsked()
        lang_names, lang_counts = self.getQuestionLanguages()
        gender_labels, gender_counts = self.getGenderStat()
        mlang_names, mlang_counts = self.getMediumLanguage()
        class_labels, class_counts = self.getStudentClassStat()
        # Stats for doughnut charts
        format_labels, format_counts = self.getQuestionFormatStats()
        curriculum_labels, curriculum_counts = self.getCurriculumStats()
        context_labels, context_counts = self.getContextStats()
        states, codes, counts = self.getMapStats()
        
        return render(request, 'public_website/analytics-home.html', 
            {"page_title": _('Analytics'), 
            "question_counter": self.getQuestionCount(),
            "lang_names" : self.fix(lang_names, apply_ = True),
            "lang_counts" : self.fix(lang_counts),
            "year_labels" : self.fix(year_labels, apply_ = True),
            "year_counts" : self.fix(year_counts),
            "gender_counts" : self.fix(gender_counts),
            "gender_labels" : self.fix(gender_labels, apply_ = True),
            "mlang_names" : self.fix(mlang_names, apply_ = True),
            "mlang_counts" : self.fix(mlang_counts),
            "class_labels" : self.fix(map(str, class_labels), apply_ = True),
            "class_counts" : self.fix(class_counts),
            "format_labels" : self.fix(format_labels, apply_ = True),
            "format_counts" : self.fix(format_counts),
            "curriculum_labels" : self.fix(curriculum_labels, apply_ = True),
            "curriculum_counts" : self.fix(curriculum_counts),
            "context_labels" : self.fix(context_labels, apply_ = True),
            "context_counts" : self.fix(context_counts),
            "state_names" : self.fix(states, apply_ = True),
            "state_codes" : self.fix(codes),
            "state_counts" : self.fix(counts),
            "languageGenderDictionary": self.getLanguageGenderDictionary(),
            "genderSubjectDictionary": self.getGenderSubjectDictionary(),
            })


    def getQuestionCount(self, params = None):
        return Question.objects.count()


    def getQuestionLanguages(self, params=None):
        distinct = Question.objects.values('language').annotate(count=Count('language'))
        lang_names = []         # list to hold the name of the language
        lang_counts = []        # list to hold the count of question for the language corresponding to name in lang_names 
        for lang in distinct:
            lang_code = lang['language']
            if lang_code in language_name:
                lang_name = language_name[lang_code]
            else:
                lang_name = lang_code

            if lang_name in lang_names:
                # if the language name is twice in the list for any reason then reject it. (Workaround)
                # Note: This is caused due to nonuniform labelling of languages in Database. 
                continue

            lang_names.append(lang_name)
            lang_counts.append(lang['count'])

        return lang_names, lang_counts


    def getYearAsked(self, params = None):
        distinct = Question.objects.values('question_asked_on').annotate(count=Count('question_asked_on'))
        year_tuples = [(tple['question_asked_on'].year if tple['question_asked_on'] else None, tple['count']) for tple in distinct ]
        year_dict = {}
        for year, count in year_tuples:
            if year is None:  #Some tuples might be None due to null value in database
                continue
            if year not in year_dict:
                year_dict[year] = count
            else:
                year_dict[year] += count
        # Now we shall generate the lists of year labels and counts
        year_label, year_count = [], []
        ordered_tuples = collections.OrderedDict(sorted(year_dict.items()))
        year_labels = list(map(str, ordered_tuples.keys()))
        year_counts = list(ordered_tuples.values())
        return year_labels, year_counts


    def getGenderStat(self, params = None):
        gender_list = ["Male", "Female", "Non-binary", ""]
        gender_data = []
        for gender in gender_list:
                gender_data.append(Question.objects.filter(student_gender = gender).count())
        return ["Male", "Female", "Non-binary", "Not known"], gender_data

    def getGenderSubjectDictionary(self, params= None):
        gender_list = ["Male", "Female", "Non-binary", ""]
        # following list is used due to inconsistent naming in database for history, philosophy and practice of science
        history_and_philosophy = [
                'History-Philosophy and Practice of Science', 
                'History - Philosophy and Practice of Science', 
                'History - Philosophy & Practice of Science', 
                'History, Philosophy & Practice of Science'
        ]

        #dictionary to hold name of the subject as the key, and all its aliases in the database in a list as the value
        non_stems_subjects = {
                'Humans & Society': ['Humans & Society'], 
                'Geography & History': ['Geography & History'], 
                'Arts & Recreation':['Arts & Recreation'], 
                'Language & Literature':['Language & Literature']
        }
        stems_subjects = {
                'Mathematics':['Mathematics'], 
                'Earth & Environment': ['Earth & Environment'], 
                'Biology': ['Biology'], 
                'Chemistry': ['Chemistry'], 
                'Physics':['Physics'], 
                'Technology & Applied Science':['Technology & Applied Science'], 
                'History, Philosophy and Practice of Science': history_and_philosophy
        }  # history/philosophy is part of STEMS : Update as per JR's comment on Zulip
           # Earth & Environment is part of STEMS
        
        genderSubjectDictionary = {'Male': {}, 'Female': {}, 'Non-binary': {}, 'Not known': {}}
        for gender in gender_list:
            for subject_name in stems_subjects:
                genderSubjectDictionary[_(gender) if gender!='' else _("Not known")][_(subject_name)]  \
                =  sum([Question.objects.filter(student_gender = gender, field_of_interest = subject_alias).count() for subject_alias in stems_subjects[subject_name]])
            
            for subject_name in non_stems_subjects:
                genderSubjectDictionary[_(gender) if gender!='' else _("Not known")][_(subject_name)]   \
                =  sum([Question.objects.filter(student_gender = gender, field_of_interest = subject_alias).count() for subject_alias in non_stems_subjects[subject_name]])

        return genderSubjectDictionary

    def getLanguageGenderDictionary(self, params = None):
        gender_list = ["Male", "Female", "Non-binary", ""]
        language_list = list(map(lambda x: x[0], Question.objects.order_by().values_list('language').distinct()))
        lang_names = [language_name[lang] if lang in language_name else lang for lang in language_list]  # get the proper names of languages
        languageGenderDictionary = {lang_name: {} for lang_name in lang_names}
        for lang_index in range(len(language_list)):
            for gender in gender_list:
                lang = language_list[lang_index]
                lang_name = lang_names[lang_index]
                languageGenderDictionary[_(lang_name)][_(gender) if gender!='' else _("Not known")] = Question.objects.filter(student_gender = gender, language = lang).count()
        return languageGenderDictionary

    def getMediumLanguage(self, params = None):
        distinct = Question.objects.values('medium_language').annotate(count=Count('medium_language'))
        mlang_names = []         # list to hold the name of the language
        mlang_counts = []        # list to hold the count of question for the language corresponding to name in lang_names 
        for lang in distinct:
            lang_code = lang['medium_language']
            if lang_code in language_name:              # This won't work here because medium is not stored using language code
                lang_name = language_name[lang_code]    # Might be useful if the database if updated and medium language is stored using code
            else:
                lang_name = lang_code
            if lang_name in mlang_names:
                # if the language name is twice in the list for any reason then reject it. (Workaround)
                continue
            if lang_name == "":         # null values for languages are captured as "Other" 
                lang_name = "Other"  
            mlang_names.append(lang_name)
            mlang_counts.append(lang['count'])
        return mlang_names, mlang_counts

    def getStudentClassStat(self, params = None):
        distinct = Question.objects.values('student_class').annotate(count=Count('student_class'))
        class_tuples = sorted([(tple['student_class'] if tple['student_class'] else "Not known", tple['count']) for tple in distinct], key = lambda item : item[0])
        # Cleaning tuples as classes are stored as 10, 10.0 ... etc
        ## Can use: clases_names = {"4,5,6": "Primary", "10,11": "Secondary", "6,7,8": "Middle School" }.update({i:i for i in range(1,13)})
        dct = {i:0 for i in range(1,13)}
        for tple in class_tuples:
            student_class = tple[0]
            student_count = tple[1]
            if student_count < 5 : # 5 is arbitrary here. Change it as per the requirements. 
                # ignore if count of student from this class is less than 5
                continue
            try:
                st_class = int(float(student_class))
            except:
                st_class = student_class
            dct[st_class] = (dct[st_class] + student_count) if st_class in dct else student_count
        return map(list, zip(*(dct.items())))


    def getQuestionFormatStats(self):
        distinct = Question.objects.values('question_format').annotate(count=Count('question_format'))
        format_tuples = sorted([(tple['question_format'] if tple['question_format'] else "Other", tple['count']) for tple in distinct], key = lambda item : item[0])
        return map(list, zip(*format_tuples))

    def getCurriculumStats(self):
        distinct = Question.objects.values('curriculum_followed').annotate(count=Count('curriculum_followed'))
        curriculum_tuples = sorted([(tple['curriculum_followed'] if tple['curriculum_followed'] else "Other", tple['count']) for tple in distinct], key = lambda item : item[0])
        return map(list, zip(*curriculum_tuples))

    def getContextStats(self):
        distinct = Question.objects.values('context').annotate(count=Count('context'))
        context_tuples = sorted([
                (tple['context'] 
                if (tple['context'] and tple['context'] != "Other (elaborate in the Notes column)") 
                else "Other", tple['count']) for tple in distinct],
            key = lambda item : item[0])
        return map(list, zip(*context_tuples))

    def getMapStats(self):
        distinct = Question.objects.values('state').annotate(count=Count('state'))    # place from where question is asked is in column state
        states, codes, counts = list(), list(), list()
        for stateCountPairDict in distinct:
            state = stateCountPairDict['state']
            if state.lower() not in self.state_code:
                continue
            states.append(state)
            codes.append(self.state_code[state.lower()])
            counts.append(stateCountPairDict['count'])
        return states, codes, counts

    def getCountryStats(self):
        ###TODO: For World Map
        pass

    @staticmethod
    def fix(lst, apply_ = False):
        """
        Method to convert the list into JSON list.
        If apply_translation is True, then map _ function to all the string values
        """
        if apply_:
            lst = list(map(_, lst))
        return json.dumps(lst)
        

class Suggestions(View):
    def get(self, request):
        lst_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ),"../assets/suggestions/")) 

        if not os.path.exists(lst_dir):
            os.makedirs(lst_dir)

        f_path = os.path.abspath(os.path.join(lst_dir, 'suggestions.csv'))

        sugg_lst = []

        if not os.path.isfile(f_path):
            ques = Question.objects.all()
            with open(f_path, 'w', newline='' , encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',')
                for i in ques:
                    if not i.question_text_english == "":
                        sugg_lst.append(i.question_text_english)
                        writer.writerow([i.question_text_english])

            return JsonResponse({"suggestion": sugg_lst})
        else:
            modTimestamp = os.path.getmtime(os.path.abspath(os.path.join(lst_dir, 'suggestions.csv')))
            modificationTime = ts.fromtimestamp(modTimestamp)             
            current_time = datetime.datetime.now() 

            if (current_time - modificationTime) > timedelta(1): 
                ques = Question.objects.all()
                with open(f_path, 'w', newline='' , encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=',')
                    for i in ques:
                        if not i.question_text_english == "":
                            sugg_lst.append(i.question_text_english)
                            writer.writerow([i.question_text_english])

                return JsonResponse({"suggestion": sugg_lst})
            else:
                with open(f_path, 'r',encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for i in reader:
                        sugg_lst.append(''.join(i))
                return JsonResponse({"suggestion": sugg_lst})
