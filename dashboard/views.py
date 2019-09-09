"""Define the functions that handle various requests by returnig a view"""

import random
import os
import urllib

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Subquery
from django.views import View
from django.http import (
    HttpResponse,
    Http404,
)
from django.contrib import messages
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
)
from django.core.paginator import Paginator

from sawaliram_auth.decorators import volunteer_permission_required
from dashboard.models import (
    QuestionArchive,
    Question,
    Answer,
    AnswerDraft,
    AnswerComment,
    UnencodedSubmission,
    Dataset)

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
            'page_title': 'Dashboard Home'
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
            'page_title': 'Submit Questions'
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
        dataset.status = 'raw'
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
            'page_title': 'Submit Questions'
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

        context = {
            'grey_background': 'True',
            'page_title': 'Manage Content',
            'datasets': datasets
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


# View Questions

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ViewQuestionsView(View):

    def get_queryset(self, request):
        '''
        Returns the queryset to use with this view (can be overridden
        by subclasses).
        '''

        return Question.objects.all()

    def get_template(self, request):
        '''
        Returns the template to render at the end (can be overridden
        by subclasses
        '''

        return 'dashboard/view-questions.html'

    def get(self, request):
        questions_set = self.get_queryset(request)

        # get values for filter
        subjects = list(questions_set.order_by()
                                     .values_list('field_of_interest', flat=True)
                                     .distinct('field_of_interest')
                                     .values_list('field_of_interest'))
        # convert list of tuples to list of strings
        subjects = [' '.join(item) for item in subjects]
        # sort the list so that longer subjects appear at the bottom
        subjects.sort(key=lambda s: len(s), reverse=True)

        states = questions_set.order_by() \
                              .values_list('state') \
                              .distinct('state') \
                              .values('state')

        curriculums = questions_set.order_by() \
                                   .values_list('curriculum_followed') \
                                   .distinct('curriculum_followed') \
                                   .values('curriculum_followed')

        # apply filters if any
        subjects_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('subject')]
        if subjects_to_filter_by:
            questions_set = questions_set.filter(field_of_interest__in=subjects_to_filter_by)

        states_to_filter_by = request.GET.getlist('state')
        if states_to_filter_by:
            questions_set = questions_set.filter(state__in=states_to_filter_by)

        curriculums_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('curriculum')]
        if curriculums_to_filter_by:
            questions_set = questions_set.filter(curriculum_followed__in=curriculums_to_filter_by)

        # sort the results if sort-by parameter exists
        # default: newest
        sort_by = request.GET.get('sort-by', 'newest')

        if sort_by == 'newest':
            questions_set = questions_set.order_by('-created_on')

        paginator = Paginator(questions_set, 15)

        page = request.GET.get('page', 1)
        questions = paginator.get_page(page)
        context = {
            'grey_background': 'True',
            'page_title': 'View Questions',
            'questions': questions,
            'subjects': subjects,
            'states': states,
            'curriculums': curriculums,
            'subjects_to_filter_by': subjects_to_filter_by,
            'states_to_filter_by': states_to_filter_by,
            'curriculums_to_filter_by': curriculums_to_filter_by,
            'result_size': questions_set.count()
        }
        return render(request, self.get_template(request), context)


# Answer Questions

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class AnswerQuestionsView(View):

    def get(self, request):
        questions_set = Question.objects.exclude(id__in=Subquery(
                                    Answer.objects.all().values('question_id')))

        # get values for filter
        subjects = list(questions_set.order_by()
                                     .values_list('field_of_interest', flat=True)
                                     .distinct('field_of_interest')
                                     .values_list('field_of_interest'))
        # convert list of tuples to list of strings
        subjects = [' '.join(item) for item in subjects]
        # sort the list so that longer subjects appear at the bottom
        subjects.sort(key=lambda s: len(s), reverse=True)

        states = questions_set.order_by() \
                              .values_list('state') \
                              .distinct('state') \
                              .values('state')

        curriculums = questions_set.order_by() \
                                   .values_list('curriculum_followed') \
                                   .distinct('curriculum_followed') \
                                   .values('curriculum_followed')

        # apply filters if any
        subjects_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('subject')]
        if subjects_to_filter_by:
            questions_set = questions_set.filter(field_of_interest__in=subjects_to_filter_by)

        states_to_filter_by = request.GET.getlist('state')
        if states_to_filter_by:
            questions_set = questions_set.filter(state__in=states_to_filter_by)

        curriculums_to_filter_by = [urllib.parse.unquote(item) for item in request.GET.getlist('curriculum')]

        if curriculums_to_filter_by:
            questions_set = questions_set.filter(curriculum_followed__in=curriculums_to_filter_by)

        # sort the results if sort-by parameter exists
        # default: newest
        sort_by = request.GET.get('sort-by', 'newest')

        if sort_by == 'newest':
            questions_set = questions_set.order_by('-created_on')

        paginator = Paginator(questions_set, 15)

        page = request.GET.get('page', 1)
        questions = paginator.get_page(page)

        context = {
            'grey_background': 'True',
            'page_title': 'Answer Questions',
            'questions': questions,
            'subjects': subjects,
            'states': states,
            'curriculums': curriculums,
            'subjects_to_filter_by': subjects_to_filter_by,
            'states_to_filter_by': states_to_filter_by,
            'curriculums_to_filter_by': curriculums_to_filter_by,
            'result_size': questions_set.count()
        }
        return render(request, 'dashboard/answer-questions.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ListUnreviewedAnswersView(ViewQuestionsView):

    def get_template(self, request):
        return 'dashboard/answers/list-unreviewed.html'

    def get_queryset(self, request):
        return Question.objects.filter(
            answers__approved_by__isnull=True,
            answers__answered_by__isnull=False,
        ).exclude(
            answers__answered_by=request.user,
        ).distinct()

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class SubmitAnswerView(View):
    def get(self, request, question_id):
        """Return the view to answer a question"""

        question_to_answer = Question.objects.get(pk=question_id)

        context = {
            'question': question_to_answer,
            'grey_background': 'True',
            'page_title': 'Submit Answer',
        }

        # Prefill draft answer, if any
        try:
            context['draft_answer'] = request.user.draft_answers.get(
                question_id=question_to_answer)

        except AnswerDraft.DoesNotExist:
            pass

        return render(request, 'dashboard/submit-answer.html', context)

    def post(self, request, question_id):
        """Save the submitted answer for review"""

        question_to_answer = Question.objects.get(pk=question_id)

        context = {
            'question': question_to_answer,
            'grey_background': 'True',
            'page_title': 'Submit Answer',
        }

        # TODO allow saving of drafts
        if request.POST.get('mode') == 'draft':
            # Save draft

            # Fetch or create draft
            draft, createdp = request.user.draft_answers.get_or_create(
                question_id=question_to_answer)

            # Update values and save
            draft.answer_text = request.POST.get('rich-text-content')
            draft.save()

            # Congratulate the user
            messages.success(request, ('Your answer has been saved.'
                'You can return to this page any time to '
                'continue editing.'))

            # Set draft in context to re-display
            context['draft_answer'] = draft

        else:
            # Submit answer

            # Create new answer object
            answer = request.user.submitted_answers.create(
                question_id=question_to_answer)

            # Save new answer
            answer.answer_text = request.POST.get('rich-text-content')
            answer.save()

            # Delete draft, if any
            try:
                draft =  request.user.draft_answers.get(
                    question_id=question_to_answer).delete()
            except AnswerDraft.DoesNotExist:
                # No drafts to delete
                pass

            # Congratulate the user
            messages.success(request, ('Thanks ' + request.user.first_name + '! Your answer will be reviewed soon!'))

        return render(request, 'dashboard/submit-answer.html', context)


# Review Answer

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ReviewAnswerView(View):

    def get(self, request, question_id, answer_id):
        """
        Return the view to approve/comment on an answer
        """

        answer = Answer.objects.get(pk=answer_id)

        context = {
            'answer': answer,
            'comments': answer.comments.all(),
            'grey_background': 'True',
        }

        return render(request, 'dashboard/answers/review.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class ApproveAnswerView(View):

    def get(self, request, question_id, answer_id):
        """
        Redirect to ReviewAnswerView
        """

        return redirect('dashboard:review-answer',
            question_id=question_id,
            answer_id=answer_id)

    def post(self, request, question_id, answer_id):
        """Mark the answer as approved"""


        try:
            answer = Answer.objects.get(pk=answer_id,
                approved_by__isnull=True)
        except Answer.DoesNotExist:
            raise Http404('Answer does not exist')

        if request.user == answer.answered_by:
            raise PermissionDenied('You cannot approve your own answer')

        if request.method != 'POST':
            return redirect('dashboard:review-answer',
                question_id=question_id,
                answer_id=answer_id)

        answer.approved_by = request.user
        answer.save()

        return redirect('dashboard:review-answers')

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

        return redirect('dashboard:review-answer',
            question_id=question_id,
            answer_id=answer_id)

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
