from django.contrib import admin
from .models import (
    Question,
    Answer,
)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['question_id__id', 'question_id__question_text']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['id', 'question_text']
    list_filter = ['language', 'state', 'field_of_interest']
