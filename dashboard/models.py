"""Define the data models for questions, answers and other components of the data."""
import datetime
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
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
	question_text = models.CharField(max_length=1000)
	question_text_english = models.CharField(max_length=1000, default='')
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


class UserManager(BaseUserManager):
	def create_user(self, email, password):
		"""
		Creates and saves a User with email and organisation
		"""
		if not email:
			raise ValueError("Email must be provided to create a user")
		email = self.normalize_email(email)
		user = self.model(email = email)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email):
		"""
		Creates and saves a user as superuser
		"""
		email = self.normalize_email(email)
		user = self.create_user(email)
		user.is_staff()
		user.is_superuser = True
		user.save()
		return user

class User(AbstractBaseUser, PermissionsMixin):
	first_name = models.CharField(max_length=30, blank=True)
	last_name = models.CharField(max_length=30, blank=True)
	email = models.EmailField(unique=True)
	is_active = models.BooleanField(default=True)
	organisation = models.CharField(max_length=200, default='')
	access_requested = models.CharField(max_length=200, default='')

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def get_full_name(self):
		"""
		Returns the first_name (we're not storing last names)
		"""
		return self.first_name

	def get_short_name(self):
		"""
		Returns the first_name
		"""
		return self.first_name
