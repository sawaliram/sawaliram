
from django.shortcuts import render
from django.http import HttpResponse

def dashboard_login(request):
    return HttpResponse("Login to access the dashboard!")