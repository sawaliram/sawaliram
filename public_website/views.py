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
from django.http import Http404
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.http import HttpResponse

from django.conf import settings

from dashboard.models import (
    Dataset,
    Answer,
    Question,
    Article,
    PublishedArticle,
    ArticleDraft,
    SubmittedArticle,
    ArticleTranslation,
    SubmittedArticleTranslation,
    SubmittedAnswerTranslation,
    AnswerTranslation,
)
from sawaliram_auth.models import User, Bookmark, Notification, Profile
from public_website.models import AnswerUserComment

import random
import urllib
from pprint import pprint


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

        search_categories = request.GET.getlist('category')

        if request.GET.getlist('questions') and not search_categories:
            search_categories.append('questions')

        if 'q' in request.GET and request.GET.get('q') != '':
            if not search_categories:
                results['questions'] = Question.objects.filter(
                            Q(question_text__icontains=request.GET.get('q')) |
                            Q(question_text_english__icontains=request.GET.get('q')) |
                            Q(school__icontains=request.GET.get('q')) |
                            Q(area__icontains=request.GET.get('q')) |
                            Q(state__icontains=request.GET.get('q')) |
                            Q(field_of_interest__icontains=request.GET.get('q')) |
                            Q(published_source__icontains=request.GET.get('q'))
                        )
                results['articles'] = PublishedArticle.objects.filter(
                            Q(title__search=request.GET.get('q')) |
                            Q(body__search=request.GET.get('q'))
                        ).order_by('-updated_on')
            else:
                if 'questions' in search_categories:
                    results['questions'] = Question.objects.filter(
                            Q(question_text__icontains=request.GET.get('q')) |
                            Q(question_text_english__icontains=request.GET.get('q')) |
                            Q(school__icontains=request.GET.get('q')) |
                            Q(area__icontains=request.GET.get('q')) |
                            Q(state__icontains=request.GET.get('q')) |
                            Q(field_of_interest__icontains=request.GET.get('q')) |
                            Q(published_source__icontains=request.GET.get('q'))
                        )
                else:
                    results['questions'] = Question.objects.none()

                if 'articles' in search_categories:
                    results['articles'] = PublishedArticle.objects.filter(
                            Q(title__search=request.GET.get('q')) |
                            Q(body__search=request.GET.get('q'))
                        ).order_by('-updated_on')
                else:
                    results['articles'] = PublishedArticle.objects.none()
        else:
            results['questions'] = Question.objects.all()
            results['articles'] = PublishedArticle.objects.all()

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

        results = self.get_querysets(request)

        result = results.get('questions')
        articles = results.get('articles')

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
        question_categories = []
        if 'questions' in request.GET:
            question_categories = request.GET.getlist('questions')

            questions_queryset = []

            if 'answered' in question_categories:
                answered_questions = result.filter(answers__approved_by__isnull=False)
                questions_queryset = answered_questions

            if 'unanswered' in question_categories:
                unanswered_questions = result.filter(answers__approved_by__isnull=True)
                if type(questions_queryset) is QuerySet:
                    questions_queryset = questions_queryset | unanswered_questions
                else:
                    questions_queryset = unanswered_questions

            result = questions_queryset

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
                          .values_list('language') \
                          .distinct('language') \
                          .values('language')

        # apply filters if any
        subjects_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('subject')]
        if subjects_to_filter_by:
            result = result.filter(field_of_interest__in=subjects_to_filter_by)

        states_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('state')]
        if states_to_filter_by:
            result = result.filter(state__in=states_to_filter_by)

        curriculums_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('curriculum')]
        if curriculums_to_filter_by:
            result = result.filter(curriculum_followed__in=curriculums_to_filter_by)

        languages_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('language')]
        if languages_to_filter_by:
            result = result.filter(language__in=languages_to_filter_by)

        # sort the results if sort-by parameter exists
        # default: newest
        sort_by = request.GET.get('sort-by', 'newest')

        if sort_by == 'newest':
            result = result.order_by('-created_on')

        # save list of IDs for Submit Answer/Review Answer
        page_title = self.get_page_title(request)
        if page_title == _('Review Answers') or page_title == _('Answer Questions'):
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
        if page_title == _('Search'):
            active_categories = request.GET.getlist('category')
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
            'grey_background': grey_background
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

        return render(request, 'public_website/article.html', context)


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
        if answer.answered_by.id != request.user.id:
            answered_question = Question.objects.get(pk=question_id)
            if answered_question.language.lower() != 'english':
                question_text = answered_question.question_text_english
            else:
                question_text = answered_question.question_text

            comment_notification = Notification(
                notification_type='comment',
                title_text=_('%(name)s left a comment on your answer') % {
                    'name': str(request.user.get_full_name()),
                },
                description_text="On your answer for the question '" + question_text + "'",
                target_url=reverse('public_website:view-answer', kwargs={'question_id': question_id, 'answer_id': answer_id}),
                user=answer.answered_by
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


class NewUserProfileView(View):

    def get(self, request, user_id):

        if not User.objects.filter(id=user_id).exists():
            raise Http404
        else:
            selected_user = User.objects.get(id=user_id)
            answer_drafts = Answer.objects.filter(submitted_by=user_id, status='draft')
            article_drafts = ArticleDraft.objects.filter(author=user_id)
            notifications = Notification.objects.filter(user=user_id)
            submitted_questions = Dataset.objects.filter(submitted_by=user_id)
            submitted_answers = Answer.objects.filter(submitted_by=user_id)
            submitted_articles = SubmittedArticle.objects.filter(author=user_id)
            published_articles = PublishedArticle.objects.filter(author=user_id)
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
                'notifications': notifications,
                'submitted_questions': submitted_questions,
                'submitted_answers': submitted_answers,
                'submitted_articles': submitted_articles,
                'published_articles': published_articles,
                'bookmarked_questions': bookmarked_questions,
                'bookmarked_articles': bookmarked_articles
            }
            return render(request, 'public_website/new-user-profile.html', context)


class UpdateUserName(View):

    def post(self, request):
        request.user.first_name = request.POST.get('first-name')
        request.user.last_name = request.POST.get('last-name')
        request.user.save()

        messages.success(request, 'Your personal info has been updated')
        return redirect('public_website:user-profile', user_id=request.user.id)


class UpdateOrganisationInfo(View):

    def post(self, request):

        if request.POST.get('organisation-name'):
            request.user.organisation = request.POST.get('organisation-name')
            request.user.save()

        if request.POST.get('organisation-role'):
            request.user.organisation_role = request.POST.get('organisation-role')
            request.user.save()

        messages.success(request, 'Your organisation info has been updated')
        return redirect('public_website:user-profile', user_id=request.user.id)


class UpdateUserPassword(View):

    def post(self, request):

        check_old_password = check_password(request.POST.get('current-password'), request.user.password)
        if check_old_password:
            if request.POST.get('new-password') == request.POST.get('confirm-new-password'):
                match_check_new = check_password(request.POST.get('new-password'), request.user.password)
                if match_check_new:
                    messages.error(request, (_('New password cannot be same as the current password')))
                else:
                    request.user.password = make_password(password=request.POST.get('new-password'))
                    request.user.save()
                    login(request, request.user)
                    messages.success(request, (_('Your password has been updated!')))
            else:
                messages.error(request, _('Make sure you entered the new password correctly both times'))
        else:
            messages.error(request, _('The password you entered is incorrect'))

        return redirect('public_website:user-profile', user_id=request.user.id)


class UpdateProfilePicture(View):

    def post(self, request):
        user_profile = Profile.objects.get(user=request.user.id)
        user_profile.profile_picture = request.POST.get('picture')
        user_profile.save()

        messages.success(request, 'Your profile picture has been updated')
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
