"""Define the View classes that handle auth requests"""

# from django.shortcuts import render
from django.http import HttpResponse
from django.views import View


class SignUpView(View):

    def get(self, request):
        return HttpResponse("SignUp")


class LoginView(View):

    def get(self, request):
        return HttpResponse("Login")
