
from django.db import models

class Question(models.Model):

    class Meta:
        db_table = 'question'

    school = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    student_name = models.CharField(max_length=100)
    student_class = models.IntegerField()
    student_age = models.IntegerField()
    question_text = models.CharField(max_length=200)
    question_topic = models.CharField(max_length=100)
    question_form = models.CharField(max_length=100)
    question_language = models.CharField(max_length=100)
    contributor = models.CharField(max_length=100)
    contributor_role = models.CharField(max_length=100)
    context = models.CharField(max_length=100)
    local_language = models.CharField(max_length=100)
    medium_language = models.CharField(max_length=100)
    question_submission_date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text