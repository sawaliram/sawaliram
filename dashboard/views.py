"""Define the functions that handle various requests by returnig a view"""

import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.http import HttpResponse
import pandas as pd
from dashboard.models import Question, User
from pprint import pprint

def get_login_view(request):
	"""Return the login view."""
	# in case 'next' is an empty string: leaving it as '' would give errors
	next_page = request.GET.get('next', '') or 'dashboard:dashboard_home'

	return render(request, 'dashboard/login.html', {
		'next_page': next_page
	})

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

	states_list = questions_superset.order_by().values_list('state').distinct('state').values('state')

	questions = questions_superset
	states_to_filter_by = request.GET.getlist('states')

	if states_to_filter_by:
		questions = questions.filter(state__in=states_to_filter_by)

	context = {
		'questions': questions,
		'states_list': states_list,
		'states_to_filter_by': states_to_filter_by,
	}
	return render(request, 'dashboard/view-questions.html', context)

def login_user(request):
	"""Log the user in"""
	email = request.POST.get('email')
	password = request.POST.get('password')
	# in case 'next' is an empty string: leaving it as '' would give errors.
	next_page = request.POST.get('next', '') or 'dashboard:dashboard_home'
	user = authenticate(request, email=email, password=password)

	if user is not None:
		login(request, user)
		return redirect(next_page)
	else:
		return render(request, 'dashboard/login.html', {
		  'error': 'Incorrect login info! Please try again',
		  'next_page': next_page,
		})

def logout_user(request):
	"""Log out the user"""
	logout(request)
	return redirect('dashboard:dashboard_home')

def signup_user(request):
	"""Create a user"""
	if request.POST.get('password') != request.POST.get('re-password'):
		return render(request, 'dashboard/signup.html', {'error': 'Passwords do not match! Please try again'})
	
	email = request.POST.get('email').strip()
	email_exists = User.objects.filter(email=email).exists()

	if email_exists:
		return render(request, 'dashboard/signup.html', {'error': 'Email already exists! Try logging in or use another email'})
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

	for i in range(len(question_text_list)):
		question = Question(
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

		question.save()

	context = {
		'number_of_questions_submitted': len(question_text_list),
	}
	return render(request, 'dashboard/questions-submitted-successfully.html', context)

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
		'Curriculum followed' : 'curriculum_followed',
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

	for index, row in file.iterrows():
		question = Question()

		for column in columns:
			column = column.strip()
			
			if not row[column] != row[column]: # check if the value is not nan

				if column == 'Published (Yes/No)':
					setattr(question, column_name_mapping[column], True if row[column] == 'Yes' else False)
				else:
					setattr(question, column_name_mapping[column], row[column].strip() if isinstance(row[column], str) else row[column])

		question.save()				
	
	return render(request, 'dashboard/excel-submitted-successfully.html')

def get_error_404_view(request, exception):
	"""Return the custom 404 page."""
	return render(request, 'dashboard/404.html')

def get_work_in_progress_view(request):
	"""Return work-in-progress view."""
	return render(request, 'dashboard/work-in-progress.html')
