"""Define the View classes that will handle the public website pages"""

from django.shortcuts import render
from django.views import View


class HomeView(View):
    def get(self, request):
        context = {
            'dashboard': 'False',
            'page_title': 'Home'
        }
        return render(request, 'public_website/home.html', context)
