"""Define the functions that handle various requests by returnig a view"""

import random
import os
import urllib

from datetime import datetime

from django.utils.translation import gettext as _

from django import forms
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import get_language_info
from django.utils.decorators import method_decorator
from django.db.models import Q, Subquery
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.views import View
from django.views.generic import (
    DetailView,
    FormView,
    UpdateView,
    DeleteView,
)
from django.http import (
    HttpResponse,
    Http404,
)
from django.contrib import messages
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    SuspiciousOperation,
    ImproperlyConfigured,
)
from django.core.cache import cache
from django.urls import reverse

from django.conf import settings

from sawaliram_auth.decorators import (
    permission_required,
    volunteer_permission_required,
)
from dashboard.models import (
    LANGUAGE_CODES,
    QuestionArchive,
    Question,
    TranslatedQuestion,
    DraftTranslatedQuestion,
    SubmittedTranslatedQuestion,
    Answer,
    AnswerCredit,
    ArticleCredit,
    AnswerTranslation,
    DraftAnswerTranslation,
    SubmittedAnswerTranslation,
    UnencodedSubmission,
    Article,
    ArticleDraft,
    SubmittedArticle,
    PublishedArticle,
    SubmittedArticle,
    ArticleTranslation,
    SubmittedArticleTranslation,
    DraftArticleTranslation,
    Comment,
    Dataset)
from sawaliram_auth.models import Notification, User, VolunteerRequest
from public_website.views import SearchView

import pandas as pd
from pprint import pprint


# Dashboard Home

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class DashboardHome(View):

    def get(self, request):
        """Return the dashboard home view."""

        tasks_stats = {
            'total_users': cache.get('total_users', 0),
            'pending_access_requests': cache.get('pending_access_requests', 0),
            'new_datasets': cache.get('new_datasets', 0),
            'submitted_articles': cache.get('submitted_articles', 0),
            'unanswered_questions': cache.get('unanswered_questions', 0),
            'unreviewed_answers': cache.get('unreviewed_answers', 0),
            'total_questions': cache.get('total_questions', 0),
            'items_to_translate': cache.get('items_to_translate', 0),
            'published_articles': cache.get('published_articles', 0),
        }
        context = {
            'page_title': _('Dashboard Home'),
            'tasks_stats': tasks_stats,
            'enable_breadcrumbs': 'Yes'
        }
        return render(request, 'dashboard/home.html', context)


# Submit Questions

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class SubmitQuestionsView(View):

    def get(self, request):
        """Return the submit questions view."""
        context = {
            'grey_background': 'True',
            'page_title': _('Submit Questions'),
            'enable_breadcrumbs': 'Yes',
        }
        return render(request, 'dashboard/submit-questions.html', context)

    def post(self, request):
        """Save dataset to archive and return success message"""

        # save the questions in the archive
        excel_sheet = pd.read_excel(request.FILES.get('excel_file'))
        columns = list(excel_sheet)

        column_name_mapping = {
            'Question': 'question_text',
            'Question Language': 'language',
            'English translation of the question': 'question_text_english',
            'How was the question originally asked?': 'question_format',
            'Context': 'context',
            'Date of asking the question': 'question_asked_on',
            'Student Name': 'student_name',
            'Gender': 'student_gender',
            'Student Class': 'student_class',
            'School Name': 'school',
            'Curriculum followed': 'curriculum_followed',
            'Medium of instruction': 'medium_language',
            'Area': 'area',
            'State': 'state',
            'Published (Yes/No)': 'published',
            'Publication Name': 'published_source',
            'Publication Date': 'published_date',
            'Notes': 'notes',
            'Contributor Name': 'contributor',
            'Contributor Role': 'contributor_role'
        }

        for index, row in excel_sheet.iterrows():
            question = QuestionArchive()

            # only save the question if the question field is non-empty
            if not row['Question'] != row['Question']:

                for column in columns:
                    column = column.strip()

                    # check if the value is not nan
                    if not row[column] != row[column]:

                        if column == 'Published (Yes/No)':
                            setattr(
                                question,
                                column_name_mapping[column],
                                True if row[column] == 'Yes' else False)
                        else:
                            setattr(
                                question,
                                column_name_mapping[column],
                                row[column].strip() if isinstance(row[column], str) else row[column])

                question.submitted_by = request.user
                question.save()

        # create an entry for the dataset
        dataset = Dataset()
        dataset.question_count = len(excel_sheet.index)
        dataset.submitted_by = request.user
        dataset.status = 'new'
        dataset.save()

        # create raw file for archiving
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_filename = 'dataset_' + str(dataset.id) + '_raw.xlsx'
        writer = pd.ExcelWriter(
            os.path.join(BASE_DIR, 'assets/submissions/raw/' + raw_filename))
        excel_sheet.to_excel(writer, 'Sheet 1')
        writer.save()

        # create file for curation
        excel_sheet['Field of Interest'] = ''
        excel_sheet['dataset_id'] = dataset.id
        uncurated_filename = 'dataset_' + str(dataset.id) + '_uncurated.xlsx'
        writer = pd.ExcelWriter(
            os.path.join(BASE_DIR, 'assets/submissions/uncurated/' + uncurated_filename))
        excel_sheet.to_excel(writer, 'Sheet 1')
        writer.save()

        messages.success(request, (_('Thank you for the questions! We will get to work preparing the questions to be answered and translated.')))
        context = {
            'grey_background': 'True',
            'page_title': _('Submit Questions'),
            'enable_breadcrumbs': 'Yes',
        }
        return render(request, 'dashboard/submit-questions.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ValidateNewExcelSheet(View):

    def post(self, request):
        """Validate excel sheet and return status/errors"""
        excel_file = pd.read_excel(request.FILES.get('excel_file'))

        file_errors = {}
        general_errors = []
        standard_columns = [
            'Question',
            'Question Language',
            'English translation of the question',
            'How was the question originally asked?',
            'Context',
            'Date of asking the question',
            'Student Name',
            'Gender',
            'Student Class',
            'School Name',
            'Curriculum followed',
            'Medium of instruction',
            'Area',
            'State',
            'Published (Yes/No)',
            'Publication Name',
            'Publication Date',
            'Notes',
            'Contributor Name',
            'Contributor Role'
        ]

        if len(list(excel_file)) != 20:
            general_errors.append('The columns of the Excel template are modified. Please use the standard template!')

        for column in list(excel_file):
            if column not in standard_columns:
                general_errors.append('"' + column + '" is not a standard column. Please use the standard template!')

        if general_errors:
            file_errors['Problem(s) with the template:'] = general_errors
            response = render(request, 'dashboard/includes/excel-validation-errors.html', {'errors': file_errors})
            return HttpResponse(response)

        for index, row in excel_file.iterrows():
            row_errors = []

            if row['Question'] != row['Question']:
                row_errors.append('Question field cannot be empty')
            if row['Question Language'] != row['Question Language']:
                row_errors.append('Question Language field cannot be empty')
            if row['Context'] != row['Context']:
                row_errors.append('Context field cannot be empty')
            if row['Published (Yes/No)'] == 'Yes' and row['Publication Name'] != row['Publication Name']:
                row_errors.append('If the question was published, you must mention the publication name')
            if row['Contributor Name'] != row['Contributor Name']:
                row_errors.append('You must mention the name of the contributor')

            if row_errors:
                # Adding 1 to compensate for 0 indexing
                file_errors['Row #' + str(index + 1)] = row_errors

        if file_errors:
            response = render(request, 'dashboard/includes/excel-validation-errors.html', {'errors': file_errors})
        else:
            response = 'validated'

        return HttpResponse(response)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class ManageUsersView(View):
    def get(self, request):
        users = User.objects.all().order_by('profile__created_on')
        all_user_count = len(users)

        access_requests = VolunteerRequest.objects.filter(status='pending')

        permissions_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('permission')]
        if permissions_to_filter_by:
            users = users.filter(groups__name__in=permissions_to_filter_by)

        filter_by_email = request.GET.get('email')
        if filter_by_email:
            if request.GET.get('email') == 'verified':
                users = users.filter(profile__email_verified=True)
            elif request.GET.get('email') == 'unverified':
                users = users.filter(Q(profile__email_verified=False) | Q(profile__isnull=True))

        sort_by = request.GET.get('sort-by', 'newest')
        if sort_by == 'newest':
            users = users.order_by('-profile__created_on')

        # remove duplicate results
        users = users.distinct()

        # search
        search_query = ''
        if 'q' in request.GET and request.GET.get('q') != '':
            search_query = request.GET.get('q')

            # search by ID
            if search_query.isdigit():
                users = users.filter(pk=int(search_query))
            else:
                # search by Name/Organisation
                keyword_list = search_query.split(' ')
                Q_object = Q(first_name__icontains=keyword_list[0]) | Q(last_name__icontains=keyword_list[0]) | Q(organisation__icontains=keyword_list[0])
                for keyword in keyword_list[1:]:
                    Q_object.add((Q(first_name__icontains=keyword_list[0]) | Q(last_name__icontains=keyword_list[0]) | Q(organisation__icontains=keyword_list[0])), Q_object.connector)
                users = users.filter(Q_object)

        # get total result size
        result_size = len(users)

        # paginate users list
        paginated_user_list = Paginator(users, 30)
        page = request.GET.get('page', 1)
        user_list_page = paginated_user_list.get_page(page)

        context = {
            'users': user_list_page,
            'all_user_count': all_user_count,
            'result_size': result_size,
            'sort_by': sort_by,
            'permissions_to_filter_by': permissions_to_filter_by,
            'filter_by_email': filter_by_email,
            'search_query': search_query,
            'access_requests': access_requests,
            'page_title': _('Manage Users'),
            'enable_breadcrumbs': 'Yes',
            'grey_background': 'True'
        }

        # get active tab
        if 'active_tab' in request.session:
            context['active_tab'] = request.session['active_tab']
            del request.session['active_tab']

        return render(request, 'dashboard/manage-users.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class ChangeUserPermissions(View):
    def post(self, request):
        granted_permissions = request.POST.getlist('granted-permissions')
        permissions = ['admins', 'reviewers', 'experts', 'writers', 'translators', 'volunteers']
        user = User.objects.get(id=request.POST.get('user-id'))

        for permission in permissions:
            if permission in granted_permissions:
                Group.objects.get(name=permission).user_set.add(user)
                # remove pending volunteer request, if any
                pending_requests = VolunteerRequest.objects \
                                                   .filter(requested_by_id=user.id) \
                                                   .filter(permissions_requested=permission) \
                                                   .filter(status='pending')
                if pending_requests:
                    for pending_request in pending_requests:
                        pending_request.status = 'processed'
                        pending_request.save()
            else:
                pass
                Group.objects.get(name=permission).user_set.remove(user)

        messages.success(request, (_('User permissions updated for ' + user.first_name + ' ' + user.last_name)))
        return redirect(request.META['HTTP_REFERER'])


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class DeleteUser(View):
    def post(self, request):
        user = User.objects.get(id=request.POST.get('user-id'))
        user.delete()

        messages.success(request, (_('User ' + user.first_name + ' ' + user.last_name + ' has been deleted')))
        return redirect(request.META['HTTP_REFERER'])


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ManageContentView(View):
    def get(self, request):

        datasets = Dataset.objects.all().order_by('-created_on')
        articles = (SubmittedArticle
            .objects.all().order_by('-updated_on'))
        article_translations = (SubmittedArticleTranslation
            .objects
            .exclude(translated_by=request.user)
            .order_by('-updated_on'))
        answer_translations = (SubmittedAnswerTranslation
            .objects
            .exclude(translated_by=request.user)
            .order_by('-updated_on'))

        context = {
            'grey_background': 'True',
            'page_title': _('Manage Content'),
            'enable_breadcrumbs': 'Yes',
            'datasets': datasets,
            'articles': articles,
            'article_translations': article_translations,
            'answer_translations': answer_translations,
        }
        return render(request, 'dashboard/manage-content.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ValidateCuratedExcelSheet(View):
    def post(self, request):
        """Validate excel sheet and return status/errors"""
        excel_file = pd.read_excel(request.FILES.get('excel_file'))

        file_errors = {}
        general_errors = []
        standard_columns = [
            'Question',
            'Question Language',
            'English translation of the question',
            'How was the question originally asked?',
            'Context',
            'Date of asking the question',
            'Student Name',
            'Gender',
            'Student Class',
            'School Name',
            'Curriculum followed',
            'Medium of instruction',
            'Area',
            'State',
            'Published (Yes/No)',
            'Publication Name',
            'Publication Date',
            'Notes',
            'Contributor Name',
            'Contributor Role',
            'Field of Interest',
            'dataset_id'
        ]

        if len(list(excel_file)) != 22:
            general_errors.append('The columns of the Excel template are modified. Please use the standard template!')

        for column in list(excel_file):
            if column not in standard_columns:
                general_errors.append('"' + column + '" is not a standard column. Please use the standard template!')

        if general_errors:
            file_errors['Problem(s) with the template:'] = general_errors

        for index, row in excel_file.iterrows():
            row_errors = []

            if row['Question'] != row['Question']:
                row_errors.append('Question field cannot be empty')
            if row['Question Language'] != row['Question Language']:
                row_errors.append('Question Language field cannot be empty')
            if len(row['Question Language']) != 2:
                row_errors.append('Question Language must be an ISO 639-1 code')
            if row['Context'] != row['Context']:
                row_errors.append('Context field cannot be empty')
            if row['Published (Yes/No)'] == 'Yes' and row['Publication Name'] != row['Publication Name']:
                row_errors.append('If the question was published, you must mention the publication name')
            if row['Contributor Name'] != row['Contributor Name']:
                row_errors.append('You must mention the name of the contributor')
            if row['Field of Interest'] != row['Field of Interest']:
                row_errors.append('Field of Interest cannot be empty')

            if row_errors:
                # Adding 1 to compensate for 0 indexing
                file_errors['Row #' + str(index + 1)] = row_errors

        if file_errors:
            response = render(request, 'dashboard/includes/excel-validation-errors.html', {'errors': file_errors})
        else:
            response = 'validated'

        return HttpResponse(response)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class CurateDataset(View):
    def post(self, request):
        """Save the data to Question table"""

        excel_sheet = pd.read_excel(request.FILES.get('excel_file'))
        columns = list(excel_sheet)

        column_name_mapping = {
            'Question': 'question_text',
            'Question Language': 'language',
            'English translation of the question': 'question_text_english',
            'How was the question originally asked?': 'question_format',
            'Context': 'context',
            'Date of asking the question': 'question_asked_on',
            'Student Name': 'student_name',
            'Gender': 'student_gender',
            'Student Class': 'student_class',
            'School Name': 'school',
            'Curriculum followed': 'curriculum_followed',
            'Medium of instruction': 'medium_language',
            'Area': 'area',
            'State': 'state',
            'Published (Yes/No)': 'published',
            'Publication Name': 'published_source',
            'Publication Date': 'published_date',
            'Notes': 'notes',
            'Contributor Name': 'contributor',
            'Contributor Role': 'contributor_role',
            'Field of Interest': 'field_of_interest',
            'dataset_id': 'dataset_id',
        }

        # verify the dataset_id
        dataset_id = list(excel_sheet['dataset_id'])[0]

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except ObjectDoesNotExist:
            messages.error(request, (_('We could not find that dataset by ID. Make sure you did not edit any other field except "Field of Interest"')))

            datasets = Dataset.objects.all().order_by('-created_on')
            context = {
                'grey_background': 'True',
                'page_title': _('Manage Content'),
                'datasets': datasets
            }
            return render(request, 'dashboard/manage-content.html', context)

        if dataset.status == 'curated':
            messages.error(request, (_('This dataset is already curated. Make sure you are uploading the correct file.')))

            datasets = Dataset.objects.all().order_by('-created_on')
            context = {
                'grey_background': 'True',
                'page_title': _('Manage Content'),
                'datasets': datasets
            }
            return render(request, 'dashboard/manage-content.html', context)

        for index, row in excel_sheet.iterrows():
            question = Question()

            for column in columns:
                column = column.strip()

                # check if the value is not nan
                if not row[column] != row[column]:

                    if column == 'Published (Yes/No)':
                        setattr(
                            question,
                            column_name_mapping[column],
                            True if row[column] == 'Yes' else False)
                    elif column == 'Field of Interest':
                        if row[column] == 'History-Philosophy & Practice of Science':
                            value = 'History, Philosophy & Practice of Science'
                        else:
                            value = row[column]
                        setattr(
                            question,
                            column_name_mapping[column],
                            value.strip() if isinstance(value, str) else value)
                    else:
                        setattr(
                            question,
                            column_name_mapping[column],
                            row[column].strip() if isinstance(row[column], str) else row[column])

            question.curated_by = request.user
            question.save()

        # update status of the dataset
        dataset.status = 'curated'
        dataset.save()

        # return to Manage Content and show success message
        messages.success(request, (_('Questions saved successfully! These will now be available for answering and translation.')))

        datasets = Dataset.objects.all().order_by('-created_on')
        context = {
            'grey_background': 'True',
            'page_title': _('Manage Content'),
            'datasets': datasets
        }
        return render(request, 'dashboard/manage-content.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ViewQuestionsView(SearchView):
    def get_querysets(self, request):
        results = {}
        results['questions'] = Question.objects.all()
        return results

    def get_page_title(self, request):
        return _('View Questions')

    def get_enable_breadcrumbs(self, request):
        return 'Yes'


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class AnswerQuestions(SearchView):
    def get_querysets(self, request):
        '''
        Returns a dict of querysets, one for each data type
        '''

        results = {}

        if hasattr(self, 'get_queryset'):
            warnings.warn('get_queryset is deprecated. Please use get_querysets instead.')

            results['questions'] = self.get_queryset(request)
            return results

        filters = self.filters
        search_categories = filters.get('search_categories', [])


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

        else:
            if 'questions' in search_categories:
                results['questions'] = Question.objects.all()
            else:
                results['questions'] = Question.objects.none()

        return results


    def set_filters(self, params):
        filters = super().set_filters(params)

        if len(filters['question_categories']) == 0:
            if 'questions' not in params:
                filters['question_categories'].append('unanswered')

        self.filters = filters
        return filters

    def get_search_query(self, request):
        """
        Returns the search query
        """
        if 'q' in request.GET:
            return request.GET.get('q')
        else:
            return ""

    def get_page_title(self, request):
        return _('Answer Questions')

    def get_enable_breadcrumbs(self, request):
        return 'Yes'



@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ReviewAnswersList(SearchView):
    def get_querysets(self, request):
        results = {}
        if 'q' in request.GET:
            query_set = Question.objects.filter(
                                answers__status='submitted',
                            ).exclude(
                                answers__submitted_by=request.user,
                            ).distinct()
            results['questions'] = query_set.filter(
                    Q(question_text__search=request.GET.get('q')) |
                    Q(question_text_english__search=request.GET.get('q')) |
                    Q(school__search=request.GET.get('q')) |
                    Q(area__search=request.GET.get('q')) |
                    Q(state__search=request.GET.get('q')) |
                    Q(field_of_interest__search=request.GET.get('q'))
            )
            return results
        else:
            ques = Question.objects.filter(
                                answers__status='submitted',
                            ).exclude(
                                answers__submitted_by=request.user,
                            ).distinct()
            temp = {}
            temp2 = []

            for q in ques:
                a = q.answers.all()   
                for ans in a:
                    comment = ans.comments.all()
                    temp[q] = comment.count()

            sorted_tuples = sorted(temp.items(), key=lambda item: item[1])
            sorted_dict = {k: v for k, v in sorted_tuples}
            
            res = sorted_dict.keys()
            for b in res:
                temp2.append(b.id)
            
            clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(temp2)])
            ordering = 'CASE %s END' % clauses

            results['questions'] = Question.objects.filter(id__in=temp2).extra(
            select={'ordering': ordering}, order_by=('ordering',))

            print(results['questions'])

            return results

    def get_page_title(self, request):
        return _('Review Answers')

    def get_enable_breadcrumbs(self, request):
        return 'Yes'


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class SubmitAnswerView(View):
    def get(self, request, question_id):
        """Return the view to answer a question"""

        # save Answer Questions URL in user session
        if 'dashboard/answer-questions' in request.META.get('HTTP_REFERER', ''):
            request.session['answer_questions_url'] = request.META.get('HTTP_REFERER')

        question_to_answer = Question.objects.get(pk=question_id)

        # get next/prev item IDs
        prev_item_id, next_item_id = '', ''
        if 'result_id_list' in request.session:
            result_id_list = request.session['result_id_list']
            if question_id in result_id_list:
                current_item_id = result_id_list.index(question_id)
                if current_item_id != 0:
                    prev_item_id = result_id_list[current_item_id - 1]
                if current_item_id != len(result_id_list) - 1:
                    next_item_id = result_id_list[current_item_id + 1]

        context = {
            'question': question_to_answer,
            'grey_background': 'True',
            'enable_breadcrumbs': 'Yes',
            'page_title': _('Submit Answer'),
            'prev_item_id': prev_item_id,
            'next_item_id': next_item_id,
            'submission_mode': 'submit'
        }

        # Prefill draft answer if in edit mode
        if request.GET.get('mode') == 'edit':
            try:
                draft_answer = Answer.objects.get(pk=request.GET.get('answer'))
                if draft_answer:
                    context['draft_answer'] = draft_answer
            except Answer.DoesNotExist:
                pass

        # Prefill draft answer, if any
        try:
            draft_answer = request.user.answers.get(
                    question_id=question_to_answer, status='draft')
            if draft_answer:
                context['draft_answer'] = draft_answer
        except Answer.DoesNotExist:
            pass

        return render(request, 'dashboard/submit-answer.html', context)

    def post(self, request, question_id):
        """Save the submitted answer for review or as draft"""

        question_to_answer = Question.objects.get(pk=question_id)

        # get next/prev item IDs
        prev_item_id, next_item_id = '', ''
        if 'result_id_list' in request.session:
            result_id_list = request.session['result_id_list']
            if question_id in result_id_list:
                current_item_id = result_id_list.index(question_id)
                if current_item_id != 0:
                    prev_item_id = result_id_list[current_item_id - 1]
                if current_item_id != len(result_id_list) - 1:
                    next_item_id = result_id_list[current_item_id + 1]

        context = {
            'question': question_to_answer,
            'grey_background': 'True',
            'enable_breadcrumbs': 'Yes',
            'prev_item_id': prev_item_id,
            'next_item_id': next_item_id,
            'page_title': _('Submit Answer'),
        }

        if request.POST.get('mode') == 'draft':
            # Save draft

            # Fetch or create draft
            draft, created = request.user.answers.get_or_create(
                question_id=question_to_answer, status='draft')

            # Update values and save
            draft.answer_text = request.POST.get('rich-text-content')
            draft.language = request.POST.get('language')
            draft.submitted_by = request.user
            draft.save()

            # Save credits
            # delete existing credits for the answer, if any
            for credit in draft.credits.all():
                credit.delete()

            credit_titles = request.POST.getlist('credit-title')
            credited_user_names = request.POST.getlist('credit-user-name')
            credited_user_ids = request.POST.getlist('credit-user-id')

            for i in range(len(credited_user_names)):
                credit = AnswerCredit()
                credit.credit_title = credit_titles[i]
                credit.credit_user_name = credited_user_names[i]
                if credited_user_ids[i]:
                    credit.is_user = True
                    credit.user = User.objects.get(pk=credited_user_ids[i])
                credit.answer = draft
                credit.save()

            # show success message to the user
            messages.success(request, (_('Your answer has been saved!'
                ' You can return to this page any time to '
                'continue editing, or go to "Drafts" in your User Profile.')))

            # Set draft in context to re-display
            context['draft_answer'] = draft

            return render(request, 'dashboard/submit-answer.html', context)

        else:

            if request.POST.get('mode') == 'edit':
                answer = Answer.objects.get(pk=request.POST.get('answer_id'))
            else:
                answer, created = request.user.answers.get_or_create(
                    question_id=question_to_answer, status='draft')
                answer.status = 'submitted'

            answer.answer_text = request.POST.get('rich-text-content')
            answer.language = request.POST.get('language')
            answer.save()

            # Save credits
            # delete existing credits for the answer, if any
            for credit in answer.credits.all():
                credit.delete()

            credit_titles = request.POST.getlist('credit-title')
            credited_user_names = request.POST.getlist('credit-user-name')
            credited_user_ids = request.POST.getlist('credit-user-id')

            for i in range(len(credited_user_names)):
                credit = AnswerCredit()
                credit.credit_title = credit_titles[i]
                credit.credit_user_name = credited_user_names[i]
                if credited_user_ids[i]:
                    credit.is_user = True
                    credit.user = User.objects.get(pk=credited_user_ids[i])
                credit.answer = answer
                credit.save()

            # show message to the user
            if request.POST.get('mode') == 'edit':
                messages.success(request, (_('Your answer has been updated!')))

                # create notifications for users who commented on the answer
                commentor_id_list = list(answer.comments.all()
                                        .values_list('author')
                                        .distinct('author'))
                for commentor_id in commentor_id_list:
                    if question_to_answer.language.lower() != 'english':
                        question_text = question_to_answer.question_text_english
                    else:
                        question_text = question_to_answer.question_text

                    edit_notification = Notification(
                        notification_type='updated',
                        title_text=str(request.user.get_full_name()) + ' updated their answer',
                        description_text="You commented on an answer for question '" + question_text + "'",
                        target_url=reverse('dashboard:review-answer', kwargs={'question_id': question_to_answer.id, 'answer_id': answer.id}),
                        user=User.objects.get(pk=max(commentor_id))
                    )
                    edit_notification.save()

            else:
                messages.success(request, (_('Thanks ' + request.user.first_name + '! Your answer will be reviewed soon!')))

            if request.POST.get('mode') == 'edit' and answer.status == 'draft':
                context['draft_answer'] = answer
                return render(request, 'dashboard/submit-answer.html', context)
            elif request.POST.get('mode') == 'edit' and answer.status == 'submitted':
                return redirect('dashboard:review-answer', question_id=question_to_answer.id, answer_id=answer.id)
            elif request.POST.get('mode') == 'submit' and next_item_id:
                question_to_answer = Question.objects.get(pk=next_item_id)
                context['prev_item_id'] = prev_item_id
                context['next_item_id'] = next_item_id
                context['question'] = question_to_answer
                return render(request, 'dashboard/submit-answer.html', context)
            else:
                return redirect('dashboard:answer-questions')


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ReviewAnswerView(View):

    def get(self, request, question_id, answer_id):
        """
        Return the view to approve/comment on an answer
        """

        # save Review Answers URL in user session
        if 'dashboard/review-answers' in request.META.get('HTTP_REFERER', ''):
            request.session['review_answers_url'] = request.META.get('HTTP_REFERER')

        answer = Answer.objects.get(pk=answer_id)

        context = {
            'answer': answer,
            'comments': answer.comments.all(),
            'comment_form': CommentForm(),
            'page_title': _('Submit Review'),
            'enable_breadcrumbs': 'Yes'
        }

        return render(request, 'dashboard/answers/review.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ApproveAnswerView(View):

    def get(self, request, question_id, answer_id):
        """
        Redirect to ReviewAnswerView
        """

        return redirect(
            'dashboard:review-answer',
            question_id=question_id,
            answer_id=answer_id)

    def post(self, request, question_id, answer_id):
        """
        Mark the answer as approved
        """

        try:
            answer = Answer.objects.get(
                pk=answer_id,
                status='submitted')
        except Answer.DoesNotExist:
            raise Http404(_('Answer does not exist'))

        if request.user == answer.submitted_by:
            raise PermissionDenied(_('You cannot approve your own answer'))

        if request.method != 'POST':
            return redirect(
                'dashboard:review-answer',
                question_id=question_id,
                answer_id=answer_id)

        answer.approved_by = request.user
        answer.status = 'published'
        answer.published_on = datetime.now()
        answer.save()

        messages.success(request, (_('Thanks ' + request.user.first_name + ' for publishing the answer, it will now be visible to all users')))

        question_answered = Question.objects.get(pk=question_id)

        # create notification for user who submitted the answer
        if question_answered.language.lower() != 'english':
            question_text = question_answered.question_text_english
        else:
            question_text = question_answered.question_text

        published_notification = Notification(
            notification_type='published',
            title_text=str(request.user.get_full_name()) + ' published your answer',
            description_text="Your answer for question '" + question_text + "'",
            target_url=reverse('public_website:view-answer', kwargs={'question_id': question_answered.id, 'answer_id': answer.id}),
            user=answer.submitted_by
        )
        published_notification.save()

        # create notifications for users who commented on the answer
        commentor_id_list = list(answer.comments.all()
          .values_list('author')
          .distinct('author'))
        for commentor_id in commentor_id_list:
            # do not create notification for the user who is publishing
            # the answer
            if max(commentor_id) != request.user.id:
                if question_answered.language.lower() != 'english':
                    question_text = question_answered.question_text_english
                else:
                    question_text = question_answered.question_text

                published_notification = Notification(
                    notification_type='published',
                    title_text=str(request.user.get_full_name()) + ' published ' + answer.submitted_by.first_name + "'s answer",
                    description_text="You commented on an answer for question '" + question_text + "'",
                    target_url=reverse('dashboard:review-answer', kwargs={'question_id': question_answered.id, 'answer_id': answer.id}),
                    user=User.objects.get(pk=max(commentor_id))
                )
                published_notification.save()

        return redirect('dashboard:review-answers')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteSubmittedAnswer(View):

    def post(self, request, answer_id):
        """
        Delete submitted answers (non-published)
        """
        try:
            answer = Answer.objects.get(
                pk=answer_id,
                status='submitted')
        except Answer.DoesNotExist:
            raise Http404(_('Answer does not exist'))

        if answer.submitted_by == request.user:
            answer.delete()
        else:
            raise PermissionDenied(_('You can only delete your own answers.'))

        messages.success(request, 'The submitted answer has been deleted')
        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='submissions')


# Write Articles
def create_article(request):
    '''
    Create a blank draft and redirect to WriteArticleView
    '''

    draft = ArticleDraft.objects.create(author=request.user)

    return redirect(reverse('dashboard:edit-article',
      kwargs={'draft_id': draft.id}))


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class EditArticleView(View):
    '''
    Write or update a draft or published article
    '''

    model = ArticleDraft
    template = 'dashboard/articles/write-article.html'
    success_message = 'Thanks! Your article has been submitted.'
    draft_save_message = 'Your changes have been saved.'

    def get_article(self, article):
        '''
        Fetch and sanitise an article
        '''

        # Get ArticleDraft or SubmittedArticle
        try:
            article = ArticleDraft.objects.get(id=article)
        except ArticleDraft.DoesNotExist:
            article = get_object_or_404(SubmittedArticle, id=article)

        # Sanitise fields so 'None' doesn't get rendered
        if article.title is None: article.title = ''
        if article.body is None: article.body = ''

        return article

    def submit_article(self, article):
        '''
        Submits the article. Override this for custom behaviour.
        '''

        return article.submit_draft()

    def get(self, request, draft_id):
        '''
        Display the edit form
        '''

        article = self.get_article(draft_id)
        article_drafts = ArticleDraft.objects.filter(author=request.user)
        context = {
            'article': article,
            'article_drafts': article_drafts,
            'grey_background': 'True',
            'page_title': _('Write Article'),
            'enable_breadcrumbs': 'Yes',
            'language_choices': settings.CONTENT_LANGUAGES,
        }

        return render(request, self.template, context)

    def post(self, request, draft_id):
        '''
        Save draft or submit post
        '''

        article = self.get_article(draft_id)
        article_drafts = ArticleDraft.objects.filter(author=request.user)
        context = {
            'article': article,
            'article_drafts': article_drafts,
            'grey_background': 'True',
            'language_choices': settings.CONTENT_LANGUAGES,
            'page_title': _('Write Article'),
            'enable_breadcrumbs': 'Yes'
        }

        article.title = request.POST.get('title')
        article.body = request.POST.get('rich-text-content')
        article.language = request.POST.get('language')

        if request.POST.get('mode') == 'draft':

            # Save credits
            # delete existing credits for the answer, if any
            for credit in article.credits.all():
                credit.delete()

            credit_titles = request.POST.getlist('credit-title')
            credited_user_names = request.POST.getlist('credit-user-name')
            credited_user_ids = request.POST.getlist('credit-user-id')

            for i in range(len(credited_user_names)):
                credit = ArticleCredit()
                credit.credit_title = credit_titles[i]
                credit.credit_user_name = credited_user_names[i]
                if credited_user_ids[i]:
                    credit.is_user = True
                    credit.user = User.objects.get(pk=credited_user_ids[i])
                credit.article = article
                credit.save()

            article.save()

            messages.success(request, self.draft_save_message)

            # if submitted, go back to reviwe page
            if article.is_submitted:
                return redirect('dashboard:review-article', article=article.id)

            return render(request, self.template, context)

        elif request.POST.get('mode') == 'submit':

            # Get and submit article
            submitted_article = self.submit_article(article)

            # Save credits
            # delete existing credits for the answer, if any
            for credit in submitted_article.credits.all():
                credit.delete()

            credit_titles = request.POST.getlist('credit-title')
            credited_user_names = request.POST.getlist('credit-user-name')
            credited_user_ids = request.POST.getlist('credit-user-id')

            for i in range(len(credited_user_names)):
                credit = ArticleCredit()
                credit.credit_title = credit_titles[i]
                credit.credit_user_name = credited_user_names[i]
                if credited_user_ids[i]:
                    credit.is_user = True
                    credit.user = User.objects.get(pk=credited_user_ids[i])
                credit.article = submitted_article
                credit.save()

            messages.success(request, self.success_message)
            return redirect('dashboard:review-article', article=submitted_article.id)

        else:
            raise SuspiciousOperation(_('Are you trying to save draft or submit?'))


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteArticleView(View):
    def fetch_article(self, article):
        """
        Return selected comment
        """

        article = get_object_or_404(ArticleDraft, id=article)

        return article

    def get(self, request, article):
        """
        Confirm whether to delete a comment or not
        """

        article = self.fetch_article(article)

        context = {
            'article': article,
        }
        return render(request, 'dashboard/articles/delete.html', context)

    def post(self, request, article):
        """
        Deletes selected draft article
        """

        article = self.fetch_article(article)

        if request.user != article.author:
            raise PermissionDenied(_('You are not authorised to delete this article.'))

        article.delete()

        messages.success(request, 'The draft article has been deleted')

        if request.POST.get('origin') == 'write-article':
            return redirect('dashboard:home')

        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='drafts')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteSubmittedArticle(View):

    def post(self, request, article_id):
        """
        Deletes submitted article
        """
        article = get_object_or_404(SubmittedArticle, id=article_id)

        if request.user != article.author:
            raise PermissionDenied(_('You can only delete your own articles.'))

        article.delete()

        messages.success(request, 'The submitted article has been deleted')
        return redirect('public_website:user-profile', user_id=request.user.id, active_tab='submissions')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class ReviewSubmittedArticleView(View):
    '''
    Add updates to a submitted article
    '''

    model = SubmittedArticle
    template = 'dashboard/articles/review.html'

    def get(self, request, article):
        article = get_object_or_404(self.model, id=article)
        context = {
            'article': article,
            'grey_background': 'True',
            'comments': article.comments.all(),
            'page_title': _('Review Article'),
            'comment_form': CommentForm(),
            'enable_breadcrumbs': 'Yes'
        }

        return render(request, self.template, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class ApproveSubmittedArticleView(View):

    model = SubmittedArticle
    success_message = 'The article has been published successfully'

    def get(self, request, article):
        '''
        Not valid; redirect user back to article
        '''
        return redirect(reverse('dashboard:review-article', kwargs={'article': article}))

    def post(self, request, article):
        article = get_object_or_404(self.model, id=article)

        # Check that the publisher is not the author
        if article.author == request.user:
            raise PermissionDenied(_('You cannot publish your own article.'))

        a = article.publish(request.user)

        messages.success(request, self.success_message)
        return redirect(a.get_absolute_url())


# Comments
class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Enter your comment...',
        'rows': '4',
    }))


class CommentMixin:
    '''
    Mixin to help create comment-handling views
    '''

    model = Comment

    def get_target(self, target_type, target):

        if target_type == 'article':
            target_model = Article
        elif target_type == 'answer':
            target_model = Answer
        elif target_type == 'article-translation':
            target_model = ArticleTranslation
        elif target_type == 'answer-translation':
            target_model = AnswerTranslation
        else:
            # What is this‽ Let's get out of here!
            raise Http404

        return get_object_or_404(target_model, id=target)

    def setup(self, request, target_type, target, *args, **kwargs):
        self.target = self.get_target(target_type, target)
        return super().setup(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class CreateCommentView(CommentMixin, FormView):
    '''
    Add a comment to any item
    '''

    form_class = CommentForm
    template_name = 'dashboard/comments/create.html'

    def get_context(self, form=None):
        if form is None:
            form = self.get_form()

        return {
            'comment': {
                'target': self.target,
                'author': self.request.user,
            },
            'form': form,
        }

    def get(self, request, target_type, target):
        return render(self.request,
            self.template_name,
            self.get_context())

    def form_valid(self, form):
        '''
        Let's create the comment!
        '''

        c = Comment.objects.create(
            text=form.cleaned_data.get('text'),
            author=self.request.user,
            target=self.target,
        )

        messages.success(self.request, 'Your comment has been posted.')

        if hasattr(self.target, 'author'):
            # Create notification for the comment

            if self.target.author != self.request.user:
                Notification.objects.create(
                    notification_type='comment',
                    title_text=('{} left a comment on your {}'
                        .format(
                            self.request.user.get_full_name(),
                            self.target._meta.verbose_name,
                        )),
                    description_text=('Commented on {}'
                        .format(self.target)),
                    target_url=self.target.get_absolute_url(),
                    user=self.target.author,
                )

        return super().form_valid(form)

    def form_invalid(self, form):
        '''
        Let's ask the user to try again!
        '''

        return render(self.request,
            self.template_name,
            self.get_context(form))

    def get_success_url(self):
        if 'next' in self.request.POST:
            return self.request.POST.get('next')
        elif 'next' in self.request.GET:
            return self.request.GET.get('next')
        else:
            return self.target.get_absolute_url()

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteCommentView(DeleteView):

    model = Comment
    template_name = 'dashboard/comments/delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Set success_url
        if not self.success_url:
            self.success_url = obj.target.get_absolute_url()

        # Carry on
        return obj

class CreateAnswerCommentView(CreateCommentView):
    def get(self, request, target_type, answer, question):
        return super().get(request, target_type, answer)

    def post(self, request, target_type, answer, question):
        return super().post(request, target_type, answer)

    def setup(self, request, target_type, answer, question):
        return super().setup(request, target_type, answer)

# Start Translation

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class TranslateAnswersList(SearchView):
    # def set_filters(self, params):
    #     filters = super().set_filters(params)
        
    #     search_categories = filters.get('search_categories', [])

    #     if not search_categories:
    #         search_categories.append('questions')
    #     print(filters)

    #     self.filters = filters
    #     return filters


    def get_querysets(self, request):
        results = {}

        filters = self.filters
        search_categories = filters.get('search_categories', [])

        if not search_categories:
            search_categories.append('questions')


        if 'q' in request.GET and request.GET.get('q') != '':
            if not search_categories:
                query_set = Question.objects.filter(
                                    answers__isnull=False,
                                    answers__status=Answer.STATUS_PUBLISHED,
                                    answers__translations__isnull=True,
                                ).distinct()

                results['questions'] = query_set.filter(
                        Q(question_text__search=request.GET.get('q')) |
                        Q(question_text_english__search=request.GET.get('q')) |
                        Q(school__search=request.GET.get('q')) |
                        Q(area__search=request.GET.get('q')) |
                        Q(state__search=request.GET.get('q')) |
                        Q(field_of_interest__search=request.GET.get('q'))
                )

                results['articles'] = (PublishedArticle.objects.filter(
                    translations__isnull=True,
                )
                .filter(
                    Q(title__search=request.GET.get('q')) |
                    Q(body__search=request.GET.get('q'))
                )
                .distinct())
            else:
                if 'questions' in search_categories:
                    results['questions'] = Question.objects.filter(
                                    answers__isnull=False,
                                    answers__status=Answer.STATUS_PUBLISHED,
                                    answers__translations__isnull=True,
                                ).distinct()
                else:
                    results['questions'] = Question.objects.none()


                if 'articles' in search_categories:
                    results['articles'] = PublishedArticle.objects.filter(
                        translations__isnull=True,
                    ).distinct()
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

    def set_filters(self, params):
        filters = super().set_filters(params)

        if len(filters['question_categories']) == 0:
            if 'questions' not in params:
                filters['question_categories'].append('answered')

        self.filters = filters
        return filters


    def get_page_title(self, request):
        return 'Translate Content'

    def get_enable_breadcrumbs(self, request):
        return 'Yes'




class TranslationLanguagesForm(forms.Form):
    '''
    Form to initiate a translation: decides "from" and "to" languages of
    the translation.
    '''

    lang_from = forms.ChoiceField(choices=settings.CONTENT_LANGUAGES,
        widget=forms.Select(attrs={
            'class': 'custom-select btn-primary',
        }))
    lang_to = forms.ChoiceField(choices=settings.CONTENT_LANGUAGES  ,
        widget=forms.Select(attrs={
            'class': 'custom-select btn-primary',
        }))


class BaseStartTranslation(FormView):
    '''
    A generic view to initiate the translation of a piece
    '''

    form_class = TranslationLanguagesForm

    def get_source(self, source):
        return get_object_or_404(self.model, id=source)

    def get_form(self):
        form = super().get_form()

        # Decide language options
        available_languages = self.answer.list_available_languages()
        unavailable_languages = []
        for l in settings.CONTENT_LANGUAGES:
            if l not in available_languages:
                unavailable_languages.append(l)

        form.fields.get('lang_from').choices = available_languages
        form.fields.get('lang_to').choices = unavailable_languages

        return form

    def get(self, request, source, *args, **kwargs):
        self.source = self.get_source(source, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, source, *args, **kwargs):
        self.source = self.get_source(source, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def get_context_data(self):
        context = super().get_context_data()
        context['source'] = self.source

        return context

    def get_success_view(self):
        if not hasattr(self, 'success_view'):
            raise ImproperlyConfigured((
                _('No success_view set. Please set the success_view '
                'property or override get_success_view.')
            ))
        return self.success_view

    def form_valid(self, form):
        return redirect(
            self.get_success_view(),
            lang_from=form.cleaned_data.get('lang_from'),
            lang_to=form.cleaned_data.get('lang_to'),
            source=self.source.id,
        )

class CreateArticleTranslation(BaseStartTranslation):
    '''
    Initiate the translation of an article
    '''

    model = PublishedArticle
    answer_model = Answer
    template_name = 'dashboard/articles/start_translation.html'
    success_view = 'dashboard:edit-article-translation'

class CreateAnswerTranslation(BaseStartTranslation):
    '''
    Initate the translation of an answer (and question)
    '''

    model = Question
    answer_model = Answer
    template_name = 'dashboard/answers/start_translation.html'
    success_view = 'dashboard:edit-answer-translation'

    def get_source(self, source, answer, *args, **kwargs):
        question = super().get_source(source, *args, **kwargs)
        self.answer = get_object_or_404(self.answer_model, id=answer)

        # Check that they match
        if self.answer.question_id != question:
            raise Http404(_('No matching answer found.'))

        return question

    def form_valid(self, form):
        return redirect(
            self.get_success_view(),
            lang_from=form.cleaned_data.get('lang_from'),
            lang_to=form.cleaned_data.get('lang_to'),
            answer=self.answer.id,
            source=self.source.id,
        )

    def get_context_data(self):
        context = super().get_context_data()
        context['answer'] = self.answer

        return context

# Translate Article
class BaseEditTranslation(UpdateView):
    '''
    A generic view that can be extended to provide translations for
    specific models.

    Expected URL parameters: source, lang_from, lang_to
    '''

    conflict_url = None
    source_model = None
    view_name = None
    default_status = None

    def get_object(self, queryset=None):
        '''
        Fetch translation object for the given source model, language,
        and current user.
        '''

        # Check validity of languages
        valid_languages = [l[0] for l in settings.CONTENT_LANGUAGES]
        lang_from = self.kwargs.get('lang_from')
        lang_to = self.kwargs.get('lang_to')
        user = self.request.user

        if lang_from not in valid_languages:
            raise Http404(_('Invalid language: {}'
                .format(lang_from)))

        if lang_to not in valid_languages:
            raise Http404(_('Invalid language: {}'
                .format(lang_to)))

        # Fetch source model
        source = get_object_or_404(self.source_model,
            id=self.kwargs.get('source'))

        # Save the source to object
        self.source = source

        # Fetch or create the translation object itself

        # Select the specific one, if it exists
        query_filters = {
            'source': source,
            'translated_by': user,
            'language': lang_to,
            'status': self.get_default_status(),
        }

        try:
            obj, createdp = (self.model.objects
                .get_or_create(**query_filters))
        except self.model.MultipleObjectsReturned:
            # Workaround: select the first object
            # TODO: handle this more systematically
            obj = self.model.objects.filter(**query_filters)[0]

        # Blank out fields if they're empty
        for field in self.fields:
            if getattr(obj, field) is None:
                setattr(obj, field, '')

        obj.source.set_language(lang_from)

        return obj

    def get_conflict_url(self):
        '''
        Returns a URL to redirect to if there is a conflict in
        translations (eg. if multiple translations exist for the same
        language for the same object).
        '''
        if self.conflict_url is None:
            raise ImproperlyConfigured((
                _('No URL to redirect to. Either provide a URL or '
                'define a get_conflict_url method on the Model.')
            ))

        return self.conflict_url

    def get_default_status(self):
        '''
        Returns the expected status of the Draftable we're translating.
        Defaults to using the set variable, if exists, or the selected
        model's STATUS_DRAFT property if it doesn't.
        '''

        if self.default_status is not None:
            return self.default_status
        else:
            return self.model.STATUS_DRAFT

    def form_valid(self, form):
        '''
        Validates form. This version inherits from UpdateView, but also
        changes the redirect URL if the "translate to" language has been
        changed.
        '''

        # Fetch parameters
        lang_to = self.request.POST.get('lang_to')
        lang_from = self.request.POST.get('lang_from')

        # Redirect to new URL if language has been changed
        if (lang_to != self.kwargs.get('lang_to') or
          lang_from != self.kwargs.get('lang_from')):
            kwargs = self.kwargs
            kwargs['lang_from'] = lang_from
            kwargs['lang_to'] = lang_to
            self.kwargs = self.get_success_url(**kwargs)

        response = super().form_valid(form)

        print(self.object.id, self.object.source)

        if self.request.POST.get('mode') == 'submit':
            # The user wants to submit, so we'll do our own
            # processing after the default "save" behaviour.

            submission = self.object.submit_draft()

            # Set source, etc. since they don't seem to be getting
            # unset or vanishing for some reason

            submission.source = self.source
            submission.translated_by = self.request.user
            submission.language = lang_to
            submission.save()

            messages.success(self.request,
                'Thanks! your draft has been submitted for review.')

            return redirect(submission.get_absolute_url())

        return response

    def get_view_name(self):
        if self.view_name is None:
            raise ImproperlyConfigured((
                _('No view name specified. Please set view_name as '
                'found in the urlconf.')
            ))

        return self.view_name

    def get_success_url(self, **kwargs):
        if not kwargs:
            kwargs = self.kwargs
        if self.success_url is None:
            self.success_url = reverse(self.get_view_name(), kwargs=kwargs)

        return self.success_url

    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except self.model.MultipleObjectsReturned:
            return redirect(self.get_conflict_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['content_language_choices'] = settings.CONTENT_LANGUAGES

        return context

# TODO: new view for "you have multiple drafts for this answer in this
# language, please choose one".

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class EditArticleTranslation(BaseEditTranslation):
    source_model = PublishedArticle
    model = DraftArticleTranslation
    fields = ['title', 'body']
    template_name = 'dashboard/translations/article_edit.html'
    view_name = 'dashboard:edit-article-translation'

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class EditAnswerTranslation(BaseEditTranslation):
    source_model = Question
    model = DraftTranslatedQuestion
    fields = Question.translatable_fields
    template_name = 'dashboard/translations/answer_edit.html'
    view_name = 'dashboard:edit-answer-translation'

    def get_object(self):
        '''
        Fetch question and its related answer.

        Note: in this function, 'question' and 'answer' are the
        translated question and answer; the original are referred to
        as the 'source' of those question and answer.
        '''

        question = super().get_object()
        lang_to = self.kwargs.get('lang_to')
        lang_from = self.kwargs.get('lang_from')

        # Get the related source answer
        source_answer = get_object_or_404(Answer,
            id=self.kwargs.get('answer'))

        # Make sure the question and answer match
        if source_answer.question_id != question.source:
            raise Http404(_('No matching answer found'))

        # Select the specific translated answer, if it exists
        # This will be saved as self.answer
        query_filters = {
            'source': source_answer,
            'translated_by': self.request.user,
            'language': lang_to,
        }

        # Fetch the translated answer and save as 'self.answer'
        try:
            answer, createdp = (DraftAnswerTranslation.objects
                .get_or_create(**query_filters))
        except DraftAnswerTranslation.MultipleObjectsReturned:
            # Workaround: select the first object
            # TODO: handle this more systematically
            answer = DraftAnswerTranslation.objects.filter(**query_filters)[0]

        # Set the language of the answer source
        answer.source.set_language(lang_from)

        # Save the answer
        self.answer = answer

        return question

    def get_context_data(self, *args, **kwargs):
        '''
        Add the answer to the render context
        '''

        context = super().get_context_data(*args, **kwargs)
        context['answer'] = self.answer
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Set answer text if it's there
        answer_text = self.request.POST.get('answer-text')
        if answer_text:
            self.answer.answer_text = answer_text
            self.answer.language = self.request.POST.get('lang_to') or self.answer.language
            self.answer.save()

        # If submitting, mark the answer as submitted for
        # review too

        if self.request.POST.get('mode') == 'submit':
            submission = self.answer.submit_draft()
            return redirect(submission.get_absolute_url())

        return response


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class EditSubmittedArticleTranslation(EditArticleTranslation):
    model = SubmittedArticleTranslation
    view_name = 'dashboard:review-article-translation'
    default_status = SubmittedArticleTranslation.STATUS_SUBMITTED

    def get_object(self):
        obj = get_object_or_404(self.model, id=self.kwargs.get('pk'))
        self.source = obj.source

        return obj

    def get_success_url(self, **kwargs):
        return reverse(self.view_name, kwargs={'pk': self.object.id})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class EditSubmittedAnswerTranslation(EditAnswerTranslation):
    model = SubmittedTranslatedQuestion
    view_name = 'dashboard:review-answer-translation'
    default_status = SubmittedArticleTranslation.STATUS_SUBMITTED

    def get_object(self):
        question = get_object_or_404(self.model, id=self.kwargs.get('pk'))
        self.source = question.source

        # Get the related source answer
        answer = get_object_or_404(AnswerTranslation,
            id=self.kwargs.get('answer'))

        # Make sure the question and answer match
        if answer.source.question_id != question.source:
            raise Http404('No matching translations found')

        self.answer = answer

        return question

    def get_success_url(self, **kwargs):
        return self.answer.get_absolute_url()

class BaseDeleteTranslation(DeleteView):
    '''
    View that checks if you're the owner of a translation before
    allowing you to delete it
    '''

    def get_success_url(self):
        if self.success_url:
            return self.success_url

        if self.object:
            return self.object.source.get_absolute_url()

        return reverse('dashboard:translate-answers')

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.translated_by != self.request.user:
            raise PermissionDenied(_("That's not your translation!"))

        return obj


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteAnswerTranslation(BaseDeleteTranslation):
    '''
    Delete the translation of an answer
    '''

    model = AnswerTranslation
    template_name = 'dashboard/translations/answer_delete.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteArticleTranslation(BaseDeleteTranslation):
    '''
    Delete the translation of an article
    '''

    model = ArticleTranslation
    template_name = 'dashboard/translations/article_delete.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteQuestionTranslation(BaseDeleteTranslation):
    '''
    Delete the translation of a question
    '''

    model = TranslatedQuestion
    template_name = 'dashboard/translations/question_delete.html'


class BaseReview(DetailView):
    '''
    Add updates to a submitted article
    '''

    def get_context_data(self, object):
        context = super().get_context_data()

        context['comments'] = object.comments.all()
        context['comment_form'] = CommentForm()

        return context

class ReviewAnswerTranslation(BaseReview):
    '''
    Review a translated answer
    '''

    model = SubmittedAnswerTranslation
    template_name = 'dashboard/translations/answer_review.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            context['question'] = (SubmittedTranslatedQuestion
            .objects
            .filter(
                source=self.object.source.question_id,
                translated_by=self.object.translated_by,
                language=self.object.language,
            )[0])
        except IndexError:
            pass

        context['source_question'] = self.object.source.question_id
        context['source_question'].set_language(
            self.request.session.get('lang', settings.DEFAULT_LANGUAGE))

        return context


class ReviewArticleTranslation(BaseReview):
    '''
    Review a translated article
    '''

    model = SubmittedArticleTranslation
    template_name = 'dashboard/translations/article_review.html'

class BaseApproveTranslation(View):

    model = None
    success_message = 'The translation has been published successfully'

    def get_object(self):
        object_pk = self.kwargs.get('pk')
        obj = get_object_or_404(self.model, pk=object_pk)
        self.object = obj
        return obj

    def get(self, request, pk):
        '''
        Not valid; redirect user back to review page
        '''
        return redirect(self.get_object()
            .get_absolute_url())

    def post(self, request, pk):
        obj = self.get_object()

        # Check that the publisher is not the author
        if obj.translated_by == request.user:
            raise PermissionDenied(_('You cannot approve your own submissions'))

        p = obj.publish(request.user)


        # Send out notifications...

        # ...to the translator
        Notification.objects.create(
            notification_type='published',
            title_text=('{} published your {}'
                .format(
                    self.request.user.get_full_name(),
                    p._meta.verbose_name,
                ))[:50], # truncate it due to character limit
            description_text=('Published {}'
                .format(p)),
            target_url = p.get_absolute_url(),
            user=p.translated_by,
        )

        # ...to the original author
        Notification.objects.create(
            notification_type='published',
            title_text=((
                '{user} translated your {source_type}'
                ' to {language}')
                .format(
                    user=p.translated_by,
                    source_type=p.source._meta.verbose_name,
                    language=(get_language_info(p.language)
                        .get('name_translated')),
                ))[:50], # truncate it due to character limit
            description_text='Translated {}'.format(p.source),
            target_url=p.get_absolute_url(),
            user=p.source.author,
        )

        # ...to the peer reviewers
        for u in set([c.author for c in p.comments.all()]):
            Notification.objects.create(
                notification_type='published',
                title_text=((
                    'The translation by {} that you commented on '
                    'has been published.')
                    .format(p.translated_by)
                    )[:50], # truncate it due to character limit
                    description_text='Translated {}'.format(p.source),
                target_url=p.get_absolute_url(),
                user=u,
            )

        # Create success message and return
        messages.success(request, self.success_message)
        return redirect(p.get_absolute_url())


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class ApproveArticleTranslation(BaseApproveTranslation):
    model = SubmittedArticleTranslation


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class ApproveAnswerTranslation(BaseApproveTranslation):
    model = SubmittedAnswerTranslation
    question_model = SubmittedTranslatedQuestion

    def get_question_object(self):
        '''
        Get the (translated) question that matches the linked
        (translated) answer.
        '''
        obj = (SubmittedTranslatedQuestion
            .objects
            .filter(
                source=self.object.source.question_id,
                translated_by=self.object.translated_by,
                language=self.object.language,
            )[0])
        self.question = obj

        return obj

    def post(self, request, pk):
        response = super().post(request, pk)

        # Also process and publish the question
        question = self.get_question_object()
        question.publish(self.request.user)

        return response

# Admin functions

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
class AdminBulkUpdateField(View):
    '''
    Prompt and bulk update a model field
    '''

    def get_model(self):
        try:
            model_type = ContentType.objects.get(
                pk=self.request.GET.get('ct'))
        except ContentType.ObjectDoesNotExist:
            raise Http404('Invalid model')

        self.model = model_type.model_class()

        return self.model

    def get_queryset(self, ids):
        model = self.get_model()
        try:
            id_list = [int(i) for i in ids.split(',')]
        except ValueError:
            id_list= []

        return model.objects.filter(pk__in=id_list)

    def get(self, request):
        context = {
            'objects': self.get_queryset(request.GET.get('ids')),
            'model_name': self.model._meta.verbose_name_plural,
            'field_name': request.GET.get('field'),
        }

        return render(
            request,
            'admin/actions/bulk_update_field.html',
            context
        )

    def post(self, request):
        new_value = request.POST.get('new_value')
        field_name = request.GET.get('field')

        if not new_value:
            return redirect(request.build_absolute_uri())

        queryset = self.get_queryset(request.GET.get('ids'))

        updated = queryset.update(**{field_name: new_value})
        messages.success(request,
            _('%s items updated successfully') % updated)

        return redirect('admin:dashboard_%s_changelist' % queryset.model.__name__.lower())


# Legacy Functions

@login_required
def get_encode_data_view(request):
    """Return the encode data view"""

    unencoded_submissions = UnencodedSubmission.objects \
        .filter(encoded=False) \
        .order_by('-created_on')

    context = {
        'unencoded_submissions': unencoded_submissions,
        'excel_file_name': 'excel' + str(random.randint(1, 999)),
    }

    return render(request, 'dashboard/encode-data.html', context)


def submit_encoded_dataset(request):
    """Save the encoding information to Question."""
    excel_sheet = pd.read_excel(request.FILES[request.POST['excel-file-name']])

    for index, row in excel_sheet.iterrows():
        question = Question.objects.get(pk=row['id'])

        question.submission_id = row['submission_id']
        question.subject_of_session = row['Subject of class/session']
        question.question_topic_relation = row['Question topic "R"elated or "U"nrelated to the topic or "S"ponteneous']
        question.motivation = row['Motivation for asking question']
        question.type_of_information = row['Type of information requested']
        question.source = row['Source']
        question.curiosity_index = row['Curiosity index']
        question.urban_or_rural = row['Urban/Rural']
        question.type_of_school = row['Type of school']
        question.comments_on_coding_rationale = row['Comments for coding rationale']
        question.encoded_by = request.user

        question.save()

    # set the UnencodedSubmission entry as curated
    unencoded_submission_entry = UnencodedSubmission \
        .objects.get(submission_id=list(excel_sheet['submission_id'])[0])
    unencoded_submission_entry.encoded = True
    unencoded_submission_entry.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


def get_error_404_view(request, exception, template_name='dashboard/404.html'):
    """Return the custom 404 page."""

    referer = request.headers.get('Referer')

    response = render(request, template_name,
        {
            'referer': referer
        })
    response.status_code = 404  # Not Found
    return response


def get_work_in_progress_view(request):
    """Return work-in-progress view."""

    response = render(request, 'dashboard/work-in-progress.html')
    response.status_code = 501  # Not Implemented
    return response
