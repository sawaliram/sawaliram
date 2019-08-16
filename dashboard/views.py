"""Define the functions that handle various requests by returnig a view"""

import random
import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Subquery
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from sawaliram_auth.decorators import volunteer_permission_required
from dashboard.models import (
    QuestionArchive,
    Question,
    Answer,
    UnencodedSubmission,
    Dataset)

import pandas as pd


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
class ManageContentView(View):
    def get(self, request):

        datasets = Dataset.objects.all().order_by('-created_on')

        context = {
            'grey_background': 'True',
            'page_title': 'Manage Content',
            'datasets': datasets
        }
        return render(request, 'dashboard/manage-content.html', context)


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


@login_required
def get_view_questions_view(request):
    """Return the 'View Questions' view after applying filters, if any."""
    questions_superset = Question.objects.all().order_by('-created_on')

    states_list = questions_superset.order_by() \
                                    .values_list('state') \
                                    .distinct('state') \
                                    .values('state')

    questions = questions_superset
    states_to_filter_by = request.GET.getlist('states')

    if states_to_filter_by:
        questions = questions.filter(state__in=states_to_filter_by)

    context = {
        'questions': questions,
        'states_list': states_list,
        'states_to_filter_by': states_to_filter_by}

    return render(request, 'dashboard/view-questions.html', context)


@login_required
def get_answer_questions_list_view(request):
    """Return the view with list of unanswered questions"""

    unanswered_questions = Question.objects.exclude(
        id__in=Subquery(Answer.objects.all().values('question_id')))

    context = {
        'unanswered_questions': unanswered_questions}

    return render(request, 'dashboard/answer-questions-list.html', context)


@login_required
def get_answer_question_view(request, question_id):
    """Return the view to answer a question"""

    question_to_answer = Question.objects.get(pk=question_id)

    context = {
        'question': question_to_answer,
        'grey_background': 'True',
        'page_title': 'Answer Question',
    }
    return render(request, 'dashboard/answer-question.html', context)


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


def submit_answer(request):
    """Save the submitted answer for review"""
    new_answer = Answer()
    new_answer.question_id = Question.objects.get(pk=request.POST['question_id'])
    new_answer.answer_text = request.POST['rich-text-content']
    new_answer.answered_by = request.user
    new_answer.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


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
