
from django.shortcuts import render
from django.http import HttpResponse

def dashboard_home(request):
    return HttpResponse("Dashboard Home")

def dashboard_login(request):
    return HttpResponse("Dashboard Login")

def dashboard_role(request, role):
    return HttpResponse(role + " Dashboard")

def dashboard_action(request, role, action):
    return HttpResponse(role + " performed " + action)