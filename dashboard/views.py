
from django.shortcuts import render
from django.http import HttpResponse

def dashboard_home(request):
    context = {}
    return render(request, 'dashboard/home.html', context)

def dashboard_login(request):
    return HttpResponse("Dashboard Login")

def dashboard_action(request, action):
    context = {}
    return render(request, 'dashboard/' + action + '.html', context)