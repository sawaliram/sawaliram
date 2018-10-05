
from django.shortcuts import render
from django.http import HttpResponse

def dashboard_home(request):
    return HttpResponse("Dashboard Home")

def dashboard_login(request):
    return HttpResponse("Dashboard Login")

def dashboard_action(request, action):
    return HttpResponse("Page to " + action)