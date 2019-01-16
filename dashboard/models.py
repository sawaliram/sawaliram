"""Define the data models for questions, answers and other components of the data."""
import datetime
from django.db import models

class Question(models.Model):
	"""Define the data model for a question."""

	class Meta:
		db_table = 'question'

	school = models.CharField(max_length=100)
	area = models.CharField(max_length=100)
	state = models.CharField(max_length=100, default='')
	student_name = models.CharField(max_length=100)
	student_gender = models.CharField(max_length=100, default='')
	student_class = models.CharField(max_length=100, default='')
	question_text = models.CharField(max_length=500)
	question_text_english = models.CharField(max_length=500, default='')
	question_topic = models.CharField(max_length=100)
	question_format = models.CharField(max_length=100)
	question_language = models.CharField(max_length=100)
	contributor = models.CharField(max_length=100)
	contributor_role = models.CharField(max_length=100)
	context = models.CharField(max_length=100)
	local_language = models.CharField(max_length=100)
	medium_language = models.CharField(max_length=100)
	curriculum_followed = models.CharField(max_length=100, default='')
	published = models.BooleanField(default=False)
	published_source = models.CharField(max_length=200, default='')
	published_date = models.DateField(default=datetime.date.today)
	question_asked_on = models.DateField(null=True)
	notes = models.CharField(max_length=1000, default='')
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.question_text
