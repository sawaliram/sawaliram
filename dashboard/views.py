
from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Question
from datetime import datetime
from pprint import pprint

def dashboard_home(request):
    context = {}
    return render(request, 'dashboard/home.html', context)

def dashboard_login(request):
    return HttpResponse("Dashboard Login")

def task_page(request, page):
    context = {}
    return render(request, 'dashboard/' + page + '.html', context)

def submit_questions(request):
	question_text_list = request.POST.getlist('question-text')
	question_language_list = request.POST.getlist('question-language')
	question_text_english_list = request.POST.getlist('question-text-english')
	student_name_list = request.POST.getlist('student-name')
	student_class_list = request.POST.getlist('student-class')

	for i in range(len(question_text_list)):
		
		question = Question(
			school = request.POST['school-name'],
			area = request.POST['area'],
			state = request.POST['state'],
			question_format = request.POST['question-format'],
			submitted_in_question_box = request.POST['question-submitted-in-box'],
			contributor = request.POST['contributor-name'],
			contributor_role = request.POST['contributor-role'],
			context = request.POST['context'],
			medium_language = request.POST['medium-language'],
			question_text = question_text_list[i],
			question_language = question_language_list[i],
			question_text_english = question_text_english_list[i],
			student_name = student_name_list[i],
			student_class = student_class_list[i] if student_class_list[i] else 0,
			question_submission_date = datetime.now(),
			published = request.POST['published'],
		)

		if (request.POST['published'] == 'True'):
			question.published_source = request.POST['published-source']
			question.published_date = request.POST['published-date']

		question.save()

	context = {
		'number_of_questions_submitted': len(question_text_list),
	}
	
	return render(request, 'dashboard/questions-submitted-successfully.html', context)

def submit_excel_sheet(request):
	return HttpResponse("This feature is still under development!")

def error_404(request, exception):
    context = {}
    return render(request, 'dashboard/404.html', context)