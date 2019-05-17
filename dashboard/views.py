"""Define the functions that handle various requests by returnig a view"""

import random
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.db.models import Max, Subquery
import pandas as pd
from dashboard.models import (
    QuestionArchive,
    Question,
    User,
    Answer,
    UncuratedSubmission,
    UnencodedSubmission)
from pprint import pprint


def get_login_view(request):
    """Return the login view."""
    return render(request, 'dashboard/login.html')


def get_signup_view(request):
    """Return the signup view."""
    return render(request, 'dashboard/signup.html')


@login_required(login_url='login/')
def get_home_view(request):
    """Return the dashboard home view."""
    context = {}
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='login/')
def get_submit_questions_view(request):
    """Return the view for submitting questions."""
    return render(request, 'dashboard/submit-questions.html')


@login_required(login_url='login/')
def get_submit_excel_sheet_view(request):
    """Return the view for submitting Excel sheet."""
    context = {
        'excel_file_name': 'excel' + str(random.randint(1, 999)),
    }
    return render(request, 'dashboard/submit-excel-sheet.html', context)


@login_required(login_url='login/')
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


@login_required(login_url='login/')
def get_answer_questions_list_view(request):
    """Return the view with list of unanswered questions"""

    unanswered_questions = Question.objects.exclude(
        id__in=Subquery(Answer.objects.all().values('question_id')))

    context = {
        'unanswered_questions': unanswered_questions}

    return render(request, 'dashboard/answer-questions-list.html', context)


@login_required(login_url='login/')
def get_answer_question_view(request, question_id):
    """Return the view to answer a question"""

    question_to_answer = Question.objects.get(pk=question_id)

    context = {
        'question': question_to_answer
    }
    return render(request, 'dashboard/answer-question.html', context)


@login_required(login_url='login/')
def get_curate_data_view(request):
    """Return the curate data view"""

    uncurated_submissions = UncuratedSubmission.objects \
        .filter(curated=False) \
        .order_by('-created_on')

    context = {
        'uncurated_submissions': uncurated_submissions,
        'excel_file_name': 'excel' + str(random.randint(1, 999)),}

    return render(request, 'dashboard/curate-data.html', context)


@login_required(login_url='login/')
def get_encode_data_view(request):
    """Return the encode data view"""

    unencoded_submissions = UnencodedSubmission.objects \
        .filter(encoded=False) \
        .order_by('-created_on')

    context = {
        'unencoded_submissions': unencoded_submissions,
        'excel_file_name': 'excel' + str(random.randint(1, 999)),}

    return render(request, 'dashboard/encode-data.html', context)


def login_user(request):
    """Log the user in"""

    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, email=email, password=password)

    if user is not None:
        login(request, user)
        return redirect(request.POST.get('next', 'dashboard:dashboard_home'))
    else:
        return render(
            request,
            'dashboard/login.html',
            {'error': 'Incorrect login info! Please try again'})


def logout_user(request):
    """Log out the user"""

    logout(request)
    return redirect('dashboard:dashboard_home')


def signup_user(request):
    """Create a user"""

    if request.POST.get('password') != request.POST.get('re-password'):
        return render(
            request,
            'dashboard/signup.html',
            {'error': 'Passwords do not match! Please try again'})

    email = request.POST.get('email').strip()
    email_exists = User.objects.filter(email=email).exists()

    if email_exists:
        return render(
            request,
            'dashboard/signup.html',
            {'error': 'Email already exists! Try logging in!'})
    else:
        password = request.POST.get('password').strip()
        organisation = request.POST.get('organisation').strip()
        access_requested = ','.join(request.POST.getlist('access_request'))

        user = User.objects.create_user(email, password)
        user.first_name = request.POST.get('first_name').strip()
        user.last_name = request.POST.get('last_name').strip()

        if organisation == 'other':
            organisation = request.POST.get('other-org')

        user.organisation = organisation
        user.access_requested = access_requested
        user.save()

        volunteers = Group.objects.get(name='volunteers')
        volunteers.user_set.add(user)

        login(request, user)
        return redirect('dashboard:dashboard_home')


def submit_questions(request):
    """Save the submitted question(s) to the database."""
    question_text_list = request.POST.getlist('question-text')
    question_language_list = request.POST.getlist('question-language')
    question_text_english_list = request.POST.getlist('question-text-english')
    student_name_list = request.POST.getlist('student-name')
    student_class_list = request.POST.getlist('student-class')

    # create an empty dataframe to generate Excel file
    submitted_questions_df = pd.DataFrame()

    submission_id = 0
    max_submission_id = QuestionArchive.objects \
                                       .all() \
                                       .aggregate(Max('submission_id'))
    if max_submission_id['submission_id__max'] is None:
        submission_id = 1
    else:
        submission_id = max_submission_id['submission_id__max'] + 1

    for index, value in enumerate(question_text_list):
        question = QuestionArchive(
            school=request.POST['school-name'],
            area=request.POST['area'],
            state=request.POST['state'],
            question_format=request.POST['question-format'],
            contributor=request.POST['contributor-name'],
            contributor_role=request.POST['contributor-role'],
            context=request.POST['context'],
            curriculum_followed=request.POST['curriculum-followed'],
            medium_language=request.POST['medium-language'],
            question_text=value,
            question_language=question_language_list[index],
            question_text_english=question_text_english_list[index],
            student_name=student_name_list[index],
            notes=request.POST['notes']
        )

        if student_class_list[index]:
            question.student_class = student_class_list[index]

        if request.POST['published'] == 'Yes':
            question.published = True
            question.published_source = request.POST['published-source']
            question.published_date = request.POST['published-date']
        else:
            question.published = False

        if request.POST['question-asked-on']:
            question.question_asked_on = request.POST['question-asked-on']

        question.submitted_by = request.user
        question.submission_id = submission_id
        question.save()

        # pop keys that won't go into the excel file
        question_dict = question.__dict__
        question_dict.pop('_state')
        question_dict.pop('submitted_by_id')
        question_dict.pop('created_on')
        question_dict.pop('updated_on')

        # rename the keys to readable names of fields
        question_dict['Question'] = question_dict.pop('question_text')
        question_dict['Question Language'] = question_dict.pop('question_language')
        question_dict['English translation of the question'] = question_dict.pop('question_text_english')
        question_dict['How was the question originally asked?'] = question_dict.pop('question_format')
        question_dict['Context'] = question_dict.pop('context')
        question_dict['Date of asking the question'] = question_dict.pop('question_asked_on')
        question_dict['Student Name'] = question_dict.pop('student_name')
        question_dict['Gender'] = question_dict.pop('student_gender')
        question_dict['Student Class'] = question_dict.pop('student_class')
        question_dict['School Name'] = question_dict.pop('school')
        question_dict['Curriculum followed'] = question_dict.pop('curriculum_followed')
        question_dict['Medium of instruction'] = question_dict.pop('medium_language')
        question_dict['Area'] = question_dict.pop('area')
        question_dict['State'] = question_dict.pop('state')
        question_dict['Published (Yes/No)'] = question_dict.pop('published')
        question_dict['Publication Name'] = question_dict.pop('published_source')
        question_dict['Publication Date'] = question_dict.pop('published_date')
        question_dict['Notes'] = question_dict.pop('notes')
        question_dict['Contributor Name'] = question_dict.pop('contributor')
        question_dict['Contributor Role'] = question_dict.pop('contributor_role')

        # create a dataframe using the dict
        question_df = pd.DataFrame(question_dict, index=[index+1])

        # add field for adding the field of interest
        question_df['Field of Interest'] = ''

        # append the dataframe with the question to the overall dataframe
        submitted_questions_df = submitted_questions_df.append(question_df)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pprint(BASE_DIR)

    excel_filename = 'uncurated_dataset_' + request.user.first_name \
        + '_' + str(submission_id) + '.xlsx'

    writer = pd.ExcelWriter(
        os.path.join(BASE_DIR, 'assets/submissions/uncurated/' + excel_filename))
    submitted_questions_df.to_excel(writer, 'Sheet 1')
    writer.save()

    # create an entry in UncuratedSubmission for the admins
    new_submission = UncuratedSubmission()
    new_submission.submission_method = 'manual entry'
    new_submission.submission_id = submission_id
    new_submission.number_of_questions = len(question_text_list)
    new_submission.excel_sheet_name = excel_filename
    new_submission.submitted_by = request.user
    new_submission.save()

    context = {
        'number_of_questions_submitted': len(question_text_list),
    }

    return render(
        request,
        'dashboard/questions-submitted-successfully.html',
        context)


def submit_excel_sheet(request):
    """Parse the excel sheet and save the data to the database."""
    excel_sheet = pd.read_excel(request.FILES[request.POST['excel-file-name']])
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
        'Contributor Role': 'contributor_role'}

    submission_id = 0
    max_submission_id = QuestionArchive.objects \
                                       .all() \
                                       .aggregate(Max('submission_id'))

    if max_submission_id['submission_id__max'] is None:
        submission_id = 1
    else:
        submission_id = max_submission_id['submission_id__max'] + 1

    number_of_questions_submitted = len(excel_sheet.index)

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
            question.submission_id = submission_id
            question.save()

    # add field for adding the field of interest
    excel_sheet['Field of Interest'] = ''
    excel_sheet['submission_id'] = submission_id

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    excel_filename = 'uncurated_dataset_' + request.user.first_name \
        + '_' + str(submission_id) + '.xlsx'

    writer = pd.ExcelWriter(
        os.path.join(BASE_DIR, 'assets/submissions/uncurated/' + excel_filename))
    excel_sheet.to_excel(writer, 'Sheet 1')
    writer.save()

    # create an entry in UncuratedSubmission for the admins
    new_submission = UncuratedSubmission()
    new_submission.submission_method = 'excel file'
    new_submission.submission_id = submission_id
    new_submission.number_of_questions = number_of_questions_submitted
    new_submission.excel_sheet = excel_filename
    new_submission.submitted_by = request.user
    new_submission.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


def submit_curated_dataset(request):
    """Save the curated questions."""
    excel_sheet = pd.read_excel(request.FILES[request.POST['excel-file-name']])
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
        'id': 'id',
        'submission_id': 'submission_id'}

    for index, row in excel_sheet.iterrows():
        curated_question = Question()

        for column in columns:
            column = column.strip()

            # check if the value is not nan
            if not row[column] != row[column]:

                if column == 'Published (Yes/No)':
                    setattr(
                        curated_question,
                        column_name_mapping[column],
                        True if row[column] == 'Yes' else False)
                else:
                    setattr(
                        curated_question,
                        column_name_mapping[column],
                        row[column].strip() if isinstance(row[column], str) else row[column])

        curated_question.curated_by = request.user
        curated_question.save()

    # set curated=True for related UncuratedSubmission entry
    submission_id = list(excel_sheet['submission_id'])[0]
    uncurated_submission_entry = UncuratedSubmission.objects \
                                                    .get(submission_id=submission_id)
    uncurated_submission_entry.curated = True
    uncurated_submission_entry.save()

    # drop columns not required for encoding
    del excel_sheet['Question Language']
    del excel_sheet['How was the question originally asked?']
    del excel_sheet['Context']
    del excel_sheet['Date of asking the question']
    del excel_sheet['Student Name']
    del excel_sheet['Gender']
    del excel_sheet['Student Class']
    del excel_sheet['Curriculum followed']
    del excel_sheet['Medium of instruction']
    del excel_sheet['Published (Yes/No)']
    del excel_sheet['Publication Name']
    del excel_sheet['Publication Date']
    del excel_sheet['Contributor Name']
    del excel_sheet['Contributor Role']

    # add columns for encoding
    excel_sheet['Subject of class/session'] = ''
    excel_sheet['Question topic "R"elated or "U"nrelated to the topic or "S"ponteneous'] = ''
    excel_sheet['Motivation for asking question'] = ''
    excel_sheet['Type of information requested'] = ''
    excel_sheet['Source'] = ''
    excel_sheet['Curiosity index'] = ''
    excel_sheet['Urban/Rural'] = ''
    excel_sheet['Type of school'] = ''
    excel_sheet['Comments for coding rationale'] = ''
    excel_sheet['submission_id'] = submission_id

    # create and save excel file for encoding
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    excel_filename = 'unencoded_dataset_' \
        + str(submission_id) + '.xlsx'

    writer = pd.ExcelWriter(os.path.join(
            BASE_DIR, 'assets/submissions/unencoded/' + excel_filename))
    excel_sheet.to_excel(writer, 'Sheet 1')
    writer.save()

    # create an UnencodedSubmission entry
    unencoded_submission = UnencodedSubmission()
    unencoded_submission.submission_id = submission_id
    unencoded_submission.number_of_questions = len(excel_sheet.index)
    unencoded_submission.excel_sheet_name = excel_filename
    unencoded_submission.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


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
