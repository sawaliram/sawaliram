
from django.shortcuts import render
from django.http import HttpResponse

def dashboard_home(request):
    context = {}
    return render(request, 'dashboard/home.html', context)

def dashboard_login(request):
    return HttpResponse("Dashboard Login")

def dashboard_page(request, page):
    context = {}
    return render(request, 'dashboard/' + page + '.html', context)

def dashboard_action(request, action):
    if action == 'save-questions':
        save_questions(request)

def save_questions(request):
    return None

def error_404(request, exception):
    context = {}
    return render(request, 'dashboard/404.html', context)