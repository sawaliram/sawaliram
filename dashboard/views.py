"""Define the functions that handle various requests by returnig a view"""

import random
import os

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Subquery, Q
from django.views import View
from django.views.generic import (
    UpdateView,
)
from django.http import (
    HttpResponse,
    Http404, # Page Not found
)
from django.contrib import messages
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    SuspiciousOperation,
    ImproperlyConfigured,
)
from django.urls import reverse

from django.conf import settings

from sawaliram_auth.decorators import (
    permission_required,
    volunteer_permission_required,
)
from dashboard.models import (
    QuestionArchive,
    Question,
    Answer,
    AnswerDraft,
    AnswerComment,
    UnencodedSubmission,
    PublishedArticle,
    ArticleDraft,
    SubmittedArticle,
    ArticleComment,
    ArticleTranslation,
    Dataset)
from sawaliram_auth.models import Notification, User
from public_website.views import SearchView

import pandas as pd
from pprint import pprint


# Dashboard Home

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class DashboardHome(View):

    def get(self, request):
        """Return the dashboard home view."""
        context = {
            'grey_background': 'True',
            'page_title': 'Dashboard Home',
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
            'page_title': 'Submit Questions',
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
            'Question Language': 'question_language',
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

        messages.success(request, 'Thank you for the questions! We will get to work preparing the questions to be answered and translated.')
        context = {
            'grey_background': 'True',
            'page_title': 'Submit Questions',
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

# Manage Content

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ManageContentView(View):
    def get(self, request):

        datasets = Dataset.objects.all().order_by('-created_on')
        articles = SubmittedArticle.objects.all().order_by('-updated_on')

        context = {
            'grey_background': 'True',
            'page_title': 'Manage Content',
            'enable_breadcrumbs': 'Yes',
            'datasets': datasets,
            'articles': articles,
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
            'Question Language': 'question_language',
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
            messages.error(request, 'We could not find that dataset by ID. Make sure you did not edit any other field except "Field of Interest"')

            datasets = Dataset.objects.all().order_by('-created_on')
            context = {
                'grey_background': 'True',
                'page_title': 'Manage Content',
                'datasets': datasets
            }
            return render(request, 'dashboard/manage-content.html', context)

        if dataset.status == 'curated':
            messages.error(request, 'This dataset is already curated. Make sure you are uploading the correct file.')

            datasets = Dataset.objects.all().order_by('-created_on')
            context = {
                'grey_background': 'True',
                'page_title': 'Manage Content',
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
        messages.success(request, 'Questions saved successfully! These will now be available for answering and translation.')

        datasets = Dataset.objects.all().order_by('-created_on')
        context = {
            'grey_background': 'True',
            'page_title': 'Manage Content',
            'datasets': datasets
        }
        return render(request, 'dashboard/manage-content.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ViewQuestionsView(SearchView):
    def get_queryset(self, request):
        if 'q' in request.GET:
            return Question.objects.filter(
                    Q(question_text__icontains=request.GET.get('q')) |
                    Q(question_text_english__icontains=request.GET.get('q')) |
                    Q(school__icontains=request.GET.get('q')) |
                    Q(area__icontains=request.GET.get('q')) |
                    Q(state__icontains=request.GET.get('q')) |
                    Q(field_of_interest__icontains=request.GET.get('q')) |
                    Q(published_source__icontains=request.GET.get('q'))
            )
        else:
            return Question.objects.all()

    def get_page_title(self, request):
        return 'View Questions'

    def get_enable_breadcrumbs(self, request):
        return 'Yes'


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class AnswerQuestions(SearchView):
    def get_queryset(self, request):
        if 'q' in request.GET:
            query_set = Question.objects.exclude(id__in=Subquery(
                                    Answer.objects.all().values('question_id')))
            return query_set.filter(
                    Q(question_text__icontains=request.GET.get('q')) |
                    Q(question_text_english__icontains=request.GET.get('q')) |
                    Q(school__icontains=request.GET.get('q')) |
                    Q(area__icontains=request.GET.get('q')) |
                    Q(state__icontains=request.GET.get('q')) |
                    Q(field_of_interest__icontains=request.GET.get('q')) |
                    Q(published_source__icontains=request.GET.get('q'))
            )
        else:
            return Question.objects.exclude(id__in=Subquery(
                                    Answer.objects.all().values('question_id')))

    def get_page_title(self, request):
        return 'Answer Questions'

    def get_enable_breadcrumbs(self, request):
        return 'Yes'


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ReviewAnswersList(SearchView):
    def get_queryset(self, request):
        if 'q' in request.GET:
            query_set = Question.objects.filter(
                                answers__approved_by__isnull=True,
                                answers__answered_by__isnull=False,
                            ).exclude(
                                answers__answered_by=request.user,
                            ).distinct()
            return query_set.filter(
                    Q(question_text__icontains=request.GET.get('q')) |
                    Q(question_text_english__icontains=request.GET.get('q')) |
                    Q(school__icontains=request.GET.get('q')) |
                    Q(area__icontains=request.GET.get('q')) |
                    Q(state__icontains=request.GET.get('q')) |
                    Q(field_of_interest__icontains=request.GET.get('q'))
            )
        else:
            return Question.objects.filter(
                            answers__approved_by__isnull=True,
                            answers__answered_by__isnull=False,
                        ).exclude(
                            answers__answered_by=request.user,
                        ).distinct()

    def get_page_title(self, request):
        return 'Review Answers'

    def get_enable_breadcrumbs(self, request):
        return 'Yes'


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class SubmitAnswerView(View):
    def get(self, request, question_id):
        """Return the view to answer a question"""

        # save Answer Questions URL in user session
        if 'dashboard/answer-questions' in request.META.get('HTTP_REFERER'):
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
            'page_title': 'Submit Answer',
            'prev_item_id': prev_item_id,
            'next_item_id': next_item_id,
            'submission_mode': 'submit'
        }

        # Prefill draft answer, if any
        try:
            context['draft_answer'] = request.user.draft_answers.get(
                question_id=question_to_answer).answer_text
        except AnswerDraft.DoesNotExist:
            pass

        # Prefill current answer if in edit mode
        if request.GET.get('mode') == 'edit':
            context['draft_answer'] = Answer.objects.get(pk=request.GET.get('answer')).answer_text
            context['submission_mode'] = 'edit'

        return render(request, 'dashboard/submit-answer.html', context)

    def post(self, request, question_id):
        """Save the submitted answer for review"""

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
            'page_title': 'Submit Answer',
        }

        if request.POST.get('mode') == 'draft':
            # Save draft

            # Fetch or create draft
            draft, createdp = request.user.draft_answers.get_or_create(
                question_id=question_to_answer)

            # Update values and save
            draft.answer_text = request.POST.get('rich-text-content')
            draft.save()

            # Congratulate the user
            messages.success(request, ('Your answer has been saved!'
                ' You can return to this page any time to '
                'continue editing, or go to "Drafts" in your User Profile.'))

            # Set draft in context to re-display
            context['draft_answer'] = draft.answer_text
            context['prev_item_id'] = prev_item_id
            context['next_item_id'] = next_item_id

            return render(request, 'dashboard/submit-answer.html', context)

        else:
            # Submit answer

            # Create new answer object
            answer, created = request.user.submitted_answers.get_or_create(
                question_id=question_to_answer)

            # Save new answer
            answer.answer_text = request.POST.get('rich-text-content')
            answer.save()

            # Delete draft, if any
            try:
                draft = request.user.draft_answers.get(
                    question_id=question_to_answer).delete()
            except AnswerDraft.DoesNotExist:
                # No drafts to delete
                pass

            # show message to the user
            if request.POST.get('mode') == 'edit':
                messages.success(request, ('Your answer has been updated!'))
            else:
                messages.success(request, ('Thanks ' + request.user.first_name + '! Your answer will be reviewed soon!'))

            # create notifications for users who commented on the answer
            commentor_id_list = list(AnswerComment.objects
                                                  .filter(answer=answer.id)
                                                  .values_list('author')
                                                  .distinct('author'))
            for commentor_id in commentor_id_list:
                if question_to_answer.question_language.lower() != 'english':
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

            # get next/prev items
            if next_item_id:
                question_to_answer = Question.objects.get(pk=next_item_id)
                context['prev_item_id'] = prev_item_id
                context['next_item_id'] = next_item_id
                context['question'] = question_to_answer
                return render(request, 'dashboard/submit-answer.html', context)
            else:
                return redirect('dashboard:answer-questions')


# Review Answer

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ReviewAnswerView(View):

    def get(self, request, question_id, answer_id):
        """
        Return the view to approve/comment on an answer
        """

        # save Review Answers URL in user session
        if 'dashboard/review-answers' in request.META.get('HTTP_REFERER'):
            request.session['review_answers_url'] = request.META.get('HTTP_REFERER')

        answer = Answer.objects.get(pk=answer_id)

        context = {
            'answer': answer,
            'comments': answer.comments.all(),
            'grey_background': 'True',
            'page_title': 'Submit Review',
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
        """Mark the answer as approved"""

        try:
            answer = Answer.objects.get(
                pk=answer_id,
                approved_by__isnull=True)
        except Answer.DoesNotExist:
            raise Http404('Answer does not exist')

        if request.user == answer.answered_by:
            raise PermissionDenied('You cannot approve your own answer')

        if request.method != 'POST':
            return redirect(
                'dashboard:review-answer',
                question_id=question_id,
                answer_id=answer_id)

        answer.approved_by = request.user
        answer.save()

        messages.success(request, ('Thanks ' + request.user.first_name + ' for publishing the answer, it will now be visible to all users'))

        question_answered = Question.objects.get(pk=question_id)

        # create notification for user who submitted the answer
        if question_answered.question_language.lower() != 'english':
            question_text = question_answered.question_text_english
        else:
            question_text = question_answered.question_text

        published_notification = Notification(
            notification_type='published',
            title_text=str(request.user.get_full_name()) + ' published your answer',
            description_text="Your answer for question '" + question_text + "'",
            target_url=reverse('public_website:view-answer', kwargs={'question_id': question_answered.id, 'answer_id': answer.id}),
            user=answer.answered_by
        )
        published_notification.save()

        # create notifications for users who commented on the answer
        commentor_id_list = list(AnswerComment.objects
                                              .filter(answer=answer.id)
                                              .values_list('author')
                                              .distinct('author'))
        for commentor_id in commentor_id_list:
            # do not create notification for the user who is publishing
            # the answer
            if max(commentor_id) != request.user.id:
                if question_answered.question_language.lower() != 'english':
                    question_text = question_answered.question_text_english
                else:
                    question_text = question_answered.question_text

                published_notification = Notification(
                    notification_type='published',
                    title_text=str(request.user.get_full_name()) + ' published ' + answer.answered_by.first_name + "'s answer",
                    description_text="You commented on an answer for question '" + question_text + "'",
                    target_url=reverse('dashboard:review-answer', kwargs={'question_id': question_answered.id, 'answer_id': answer.id}),
                    user=User.objects.get(pk=max(commentor_id))
                )
                published_notification.save()

        return redirect('dashboard:review-answers')

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
    template = 'dashboard/articles/edit.html'
    success_message = 'Thanks! Your article has been submitted.'
    draft_save_message = 'Your changes have been saved.'

    def submit_article(self, article):
        '''
        Submits the article. Override this for custom behaviour.
        '''

        return article.submit_draft()

    def get(self, request, draft_id):
        '''
        Display the edit form
        '''

        article = get_object_or_404(self.model, id=draft_id)
        context = {
            'article': article,
            'grey_background': 'True',
            'language_choices': settings.LANGUAGE_CHOICES,
        }

        return render(request, self.template, context)

    def post(self, request, draft_id):
        '''
        Save draft or submit post
        '''

        article = get_object_or_404(self.model, id=draft_id)
        context = {
            'article': article,
            'grey_background': 'True',
            'language_choices': settings.LANGUAGE_CHOICES,
        }

        article.title = request.POST.get('title')
        article.body = request.POST.get('rich-text-content')
        article.language = request.POST.get('language')

        if request.POST.get('mode') == 'draft':

            article.save()

            messages.info(request, self.draft_save_message)
            return render(request, self.template, context)

        elif request.POST.get('mode') == 'submit':

            # Get and submit article
            submitted_article = self.submit_article(article)

            messages.success(request, self.success_message)
            return redirect(reverse('dashboard:home'))

        else:
            raise SuspiciousOperation('Are you trying to save draft or submit?')


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
        Delete a previously published comment on an answer
        """

        article = self.fetch_article(article)

        if request.user != article.author:
            raise PermissionDenied('You are not authorised to delete that comment.')

        article.delete()

        return redirect('dashboard:home')

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('admins'), name='dispatch')
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
        a = article.publish(request.user)

        messages.success(request, self.success_message)
        return redirect(reverse('dashboard:home'))

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class AddArticleCommentView(View):
    '''
    Add a comment on an article
    '''

    model = SubmittedArticle
    comment_model = ArticleComment

    def get(self, request, article):
        '''
        Not valid; redirect user back to article
        '''
        return redirect(reverse('dashboard:review-article', kwargs={'article': article}))

    def post(self, request, article):
        """
        Save the submitted comment to a particular answer
        """

        article = get_object_or_404(self.model, id=article)

        comment = self.comment_model()
        comment.text = request.POST['comment-text']
        comment.article = article
        comment.author = request.user
        comment.save()

        # create notification
        if article.author != request.user:
            answered_question = Question.objects.get(pk=question_id)

            comment_notification = Notification(
                notification_type='comment',
                title_text=str(request.user.get_full_name()) + ' left a comment on your article',
                description_text=('{} commented on {}'
                    .format(request.user.get_full_name(), article.title)),
                target_url=reverse('dashboard:review-article',
                    article=article),
                user=article.author
            )
            comment_notification.save()

        return redirect(
            'dashboard:review-article',
            article=article.id,
        )

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class DeleteArticleCommentView(View):
    def fetch_comment(self, article, comment_id):
        """
        Return selected comment
        """

        article = get_object_or_404(SubmittedArticle, id=article)

        try:
            comment = article.comments.get(pk=comment_id)
        except ArticleComment.DoesNotExist:
            raise Http404('No matching comment')

        return comment

    def get(self, request, article, comment_id):
        """
        Confirm whether to delete a comment or not
        """

        comment = self.fetch_comment(article, comment_id)

        context = {
            'comment': comment,
        }
        return render(request, 'dashboard/articles/delete_comment.html', context)

    def post(self, request, article, comment_id):
        """
        Delete a previously published comment on an answer
        """

        comment = self.fetch_comment(article, comment_id)

        if request.user != comment.author:
            raise PermissionDenied('You are not authorised to delete that comment.')

        comment.delete()

        return redirect('dashboard:review-article',
            article=article)

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

    def get_object(self, queryset=None):
        '''
        Fetch translation object for the given source model, language,
        and current user.
        '''

        # Check validity of languages
        valid_languages = [l[0] for l in settings.LANGUAGES]
        lang_from = self.kwargs.get('lang_from')
        lang_to = self.kwargs.get('lang_to')

        if lang_from not in valid_languages:
            raise Http404('Invalid language: {}'
                .format(lang_from))

        if lang_to not in valid_languages:
            raise Http404('Invalid language: {}'
                .format(lang_to))

        # Fetch source model
        source = get_object_or_404(self.source_model,
            id=self.kwargs.get('source'))

        # Fetch or create the translation object itself

        query_filters = {
            'article': source,
            'translated_by': self.request.user,
            'language': lang_to,
        }

        try:
            obj, createdp = (self.model.objects
                .get_or_create(**query_filters))
        except self.model.MultipleObjectsReturned:
            # Workaround: select the first object
            # TODO: handle this more systematically
            obj = self.model.objects.filter(**query_filters)[0]

        obj.article.set_language(lang_from)

        return obj

    def get_conflict_url(self):
        '''
        Returns a URL to redirect to if there is a conflict in
        translations (eg. if multiple translations exist for the same
        language for the same object).
        '''
        if self.conflict_url is None:
            raise ImproperlyConfigured((
                'No URL to redirect to. Either provide a URL or '
                'define a get_conflict_url method on the Model.'
            ))

        return self.conflict_url

    def form_valid(self, form):
        '''
        Validates form. This version inherits from UpdateView, but also
        changes the redirect URL if the "translate to" language has been
        changed.
        '''

        clean = form.cleaned_data

        # Redirect to new URL if language has been changed
        if (clean.get('language') != self.kwargs.get('lang_to') or
          self.request.POST.get('lang_from') != self.kwargs.get('lang_from')):
            self.success_url = reverse(
                self.get_view_name(),
                kwargs={
                    'lang_from': self.request.POST.get('lang_from'),
                    'lang_to': clean.get('language'),
                    'source': self.kwargs.get('source'),
                })
        return super().form_valid(form)

    def get_view_name(self):
        if self.view_name is None:
            raise ImproperlyConfigured((
                'No view name specified. Please set view_name as '
                'found in the urlconf.'
            ))

        return self.view_name

    def get_success_url(self):
        if self.success_url is None:
            self.success_url = reverse(self.get_view_name(), kwargs=self.kwargs)

        return self.success_url

    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except self.model.MultipleObjectsReturned:
            return redirect(self.get_conflict_url())

# TODO: new view for "you have multiple drafts for this answer in this
# language, please choose one".

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('volunteers'), name='dispatch')
class EditArticleTranslation(BaseEditTranslation):
    source_model = PublishedArticle
    model = ArticleTranslation
    fields = ['language', 'title', 'body']
    template_name = 'dashboard/translations/article_edit.html'
    view_name = 'dashboard:edit-article-translation'

    def get_object(self, *args, **kwargs):
        '''
        Fetch this user's translation object
        '''

        obj = super().get_object(*args, **kwargs)

        # Replace None with empty string
        if obj.title == None: obj.title = ''
        if obj.body == None: obj.body = ''

        return obj

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

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class AnswerCommentView(View):

    def post(self, request, question_id, answer_id):
        """
        Save the submitted comment to a particular answer
        """

        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            raise Http404('Answer does not exist')

        comment = AnswerComment()
        comment.text = request.POST['comment-text']
        comment.answer = answer
        comment.author = request.user
        comment.save()

        # create notification
        if answer.answered_by.id != request.user.id:
            answered_question = Question.objects.get(pk=question_id)
            if answered_question.question_language.lower() != 'english':
                question_text = answered_question.question_text_english
            else:
                question_text = answered_question.question_text

            comment_notification = Notification(
                notification_type='comment',
                title_text=str(request.user.get_full_name()) + ' left a comment on your answer',
                description_text="On your answer for the question '" + question_text + "'",
                target_url=reverse('dashboard:review-answer', kwargs={'question_id':question_id, 'answer_id':answer_id}),
                user=answer.answered_by
            )
            comment_notification.save()

        return redirect(
            'dashboard:review-answer',
            question_id=question_id,
            answer_id=answer_id
            )


class AnswerCommentDeleteView(View):

    def fetch_comment(self, question_id, answer_id, comment_id):
        """
        Return selected comment
        """

        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotexist:
            raise Http404('Answer does not exist')
    
        try:
            comment = answer.comments.get(pk=comment_id)
        except AnswerComment.DoesNotExist:
            raise Http404('No matching comment')

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
            raise PermissionDenied('You are not authorised to delete that comment.')

        comment.delete()

        return redirect('dashboard:review-answer',
            question_id=question_id,
            answer_id=answer_id)


def get_error_404_view(request, exception):
    """Return the custom 404 page."""

    response = render(request, 'dashboard/404.html')
    response.status_code = 404  # Not Found
    return response


def get_work_in_progress_view(request):
    """Return work-in-progress view."""

    response = render(request, 'dashboard/work-in-progress.html')
    response.status_code = 501  # Not Implemented
    return response
