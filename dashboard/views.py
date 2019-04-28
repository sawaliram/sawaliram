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
    AnswerComment,
    UncuratedSubmission)
from pprint import pprint
from django.http import (
    HttpResponse,
    Http404,
)
from django.core.exceptions import (
    PermissionDenied,
)


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
def get_manage_data_view(request):
    """Return the manage data view"""

    uncurated_submissions = UncuratedSubmission.objects \
        .filter(curated=False) \
        .order_by('-created_on')

    context = {
        'uncurated_submissions': uncurated_submissions,
        'excel_file_name': 'excel' + str(random.randint(1, 999)),}

    return render(request, 'dashboard/manage-data.html', context)


@login_required(login_url='login/')
def get_review_answers_list_view(request):
    """Return the view with list of unreviewed answers"""

    unreviewed_answers = Answer.objects \
    .filter(approved_by__isnull=True) \
    .select_related()
	
    context = {
        'unreviewed_answers': unreviewed_answers,
    }

    return render(request, 'dashboard/answers/list-unreviewed.html', context)

@login_required(login_url='login/')
def get_review_answer_view(request, answer_id):
    """Return the view to approve/comment on an answer"""

    answer = Answer.objects.get(pk=answer_id)

    context = {
        'answer': answer,
        'comments': answer.comments.all(),
    }

    return render(request, 'dashboard/answers/review.html', context)

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

    for i in range(len(question_text_list)):
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
            question_text=question_text_list[i],
            question_language=question_language_list[i],
            question_text_english=question_text_english_list[i],
            student_name=student_name_list[i],
            student_class=student_class_list[i] if student_class_list[i] else 0,
            notes=request.POST['notes']
        )

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

        # create dataframe with additional meta for curation
        question_dict = question.__dict__
        # pop keys that won't go into the excel file
        question_dict.pop('_state')
        question_dict.pop('created_on')
        question_dict.pop('updated_on')
        question_df = pd.DataFrame(question.__dict__, index=[0])

        question_df['Field of Interest'] = ''

        # append the dataframe with the question to the overall dataframe
        submitted_questions_df = submitted_questions_df.append(question_df)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    excel_filename = 'dataset_' + request.user.first_name \
        + '_' + str(submission_id) + '.xlsx'

    writer = pd.ExcelWriter(
        os.path.join(BASE_DIR, 'assets/submissions/' + excel_filename))
    submitted_questions_df.to_excel(writer, 'Sheet 1')
    writer.save()

    # create an entry in UncuratedSubmission for the admins
    new_submission = UncuratedSubmission()
    new_submission.submission_method = 'excel file'
    new_submission.submission_id = submission_id
    new_submission.number_of_questions = len(question_text_list)
    new_submission.excel_sheet = excel_filename
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
    file = pd.read_excel(request.FILES[request.POST['excel-file-name']])
    columns = list(file)

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

    number_of_questions_submitted = len(file.index)

    for index, row in file.iterrows():
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

    # create Excel sheet with additional meta for curation
    file['Field of Interest'] = ''

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    excel_filename = 'dataset_' + request.user.first_name \
        + '_' + str(submission_id) + '.xlsx'

    writer = pd.ExcelWriter(
        os.path.join(BASE_DIR, 'assets/submissions/' + excel_filename))
    file.to_excel(writer, 'Sheet 1')
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
    """Save the curated questions"""
    excel_file = pd.read_excel(request.FILES[request.POST['excel-file-name']])
    columns = list(excel_file)

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
        'Field of Interest': 'question_topic',
        'Motivation': 'motivation',
        'Type of Information': 'type_of_information',
        'Source': 'source',
        'Curiosity Index': 'curiosity_index',
        'Urban/Rural': 'urban_or_rural',
        'submission_id': 'submission_id'}

    for index, row in excel_file.iterrows():
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
    submission_id_of_curated_submission = list(excel_file['submission_id'])[0]
    uncurated_submission_entry = UncuratedSubmission.objects \
                                                    .get(submission_id=submission_id_of_curated_submission)
    uncurated_submission_entry.curated = True
    uncurated_submission_entry.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


def submit_answer(request):
    """Save the submitted answer for review"""
    new_answer = Answer()
    new_answer.question_id = Question.objects.get(pk=request.POST['question_id'])
    new_answer.answer_text = request.POST['rich-text-content']
    new_answer.answered_by = request.user
    new_answer.save()
    # pprint(request.POST['rich-text-content'])

    return render(request, 'dashboard/excel-submitted-successfully.html')

@login_required(login_url='login/')
def submit_answer_comment(request, answer_id):
    """Save the submitted comment to a particular answer"""

    # TODO: Check permissions

    try:
        answer = Answer.objects.get(pk=answer_id)
    except Answer.DoesNotExist:
        raise Http404('Answer does not exist')

    comment = AnswerComment()
    comment.text = request.POST['comment-text']
    comment.answer = answer
    comment.author = request.user

    comment.save()

    return redirect('dashboard:review-answer', answer_id=answer_id)

@login_required(login_url='login/')
def submit_answer_approval(request, answer_id):
    """Mark the answer as approved"""

    # TODO: check permissions

    try:
        answer = Answer.objects.get(pk=answer_id,
            approved_by__isnull=True)
    except Answer.DoesNotExist:
        raise Http404('Answer does not exist')

    if request.user == answer.answered_by:
        raise PermissionDenied('You cannot approve your own answer')

    answer.approved_by = request.user
    answer.save()

    return redirect('dashboard:review-answers')

def get_error_404_view(request, exception):
    """Return the custom 404 page."""
    return render(request, 'dashboard/404.html')


def get_work_in_progress_view(request):
    """Return work-in-progress view."""
    return render(request, 'dashboard/work-in-progress.html')
