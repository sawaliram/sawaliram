"""Define the data models for all Sawaliram content"""

import datetime
from django.db import models


class Dataset(models.Model):
    """Define the data model for submitted datasets"""

    question_count = models.CharField(max_length=100)
    submitted_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='submitted_datasets',
        on_delete=models.PROTECT)
    status = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class QuestionArchive(models.Model):
    """Define the data model for raw submissions by volunteers"""

    class Meta:
        db_table = 'question_archive'

    school = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='')
    student_name = models.CharField(max_length=100)
    student_gender = models.CharField(max_length=100, default='')
    student_class = models.CharField(max_length=100, default='')
    question_text = models.CharField(max_length=1000)
    question_text_english = models.CharField(max_length=1000, default='')
    question_format = models.CharField(max_length=100)
    question_language = models.CharField(max_length=100)
    contributor = models.CharField(max_length=100)
    contributor_role = models.CharField(max_length=100)
    context = models.CharField(max_length=100)
    medium_language = models.CharField(max_length=100)
    curriculum_followed = models.CharField(max_length=100, default='')
    published = models.BooleanField(default=False)
    published_source = models.CharField(max_length=200, default='')
    published_date = models.DateField(default=datetime.date.today)
    question_asked_on = models.DateField(null=True)
    notes = models.CharField(max_length=1000, default='')
    submitted_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='archived_questions',
        on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text


class Question(models.Model):
    """Define the data model for questions curated by admins."""

    class Meta:
        db_table = 'question'

    school = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='')
    student_name = models.CharField(max_length=100)
    student_gender = models.CharField(max_length=100, default='')
    student_class = models.CharField(max_length=100, default='')
    question_text = models.CharField(max_length=1000)
    question_format = models.CharField(max_length=100)
    question_language = models.CharField(max_length=100)
    contributor = models.CharField(max_length=100)
    contributor_role = models.CharField(max_length=100)
    context = models.CharField(max_length=100)
    medium_language = models.CharField(max_length=100)
    curriculum_followed = models.CharField(max_length=100, default='')
    published = models.BooleanField(default=False)
    published_source = models.CharField(max_length=200, default='')
    published_date = models.DateField(default=datetime.date.today)
    question_asked_on = models.DateField(null=True)
    notes = models.CharField(max_length=1000, default='')
    dataset_id = models.CharField(max_length=100, default='')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    curated_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='curated_questions',
        on_delete=models.PROTECT,
        default='')
    encoded_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='encoded_questions',
        on_delete=models.PROTECT,
        default='',
        blank=True,
        null=True)
    # data members for encoding
    field_of_interest = models.CharField(max_length=100, default='')
    subject_of_session = models.CharField(max_length=100, default='')
    question_topic_relation = models.CharField(max_length=100, default='')
    motivation = models.CharField(max_length=100, default='')
    type_of_information = models.CharField(max_length=100, default='')
    source = models.CharField(max_length=100, default='')
    curiosity_index = models.CharField(max_length=100, default='')
    urban_or_rural = models.CharField(max_length=100, default='')
    type_of_school = models.CharField(max_length=100, default='')
    comments_on_coding_rationale = models.CharField(max_length=500, default='')

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    """Define the data model for answers in English"""

    class Meta:
        db_table = 'answer'

    answer_text = models.TextField()
    question_id = models.ForeignKey(
        'Question',
        related_name='answers',
        on_delete=models.PROTECT,
        default='')
    answered_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='submitted_answers',
        on_delete=models.PROTECT,
        default='')
    approved_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='approved_answers',
        on_delete=models.PROTECT,
        default='',
        null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class UncuratedSubmission(models.Model):
    """Define the data model to store submissions pending for curation"""

    class Meta:
        db_table = 'uncurated_submission'

    submission_method = models.CharField(max_length=50)
    submission_id = models.IntegerField()
    number_of_questions = models.IntegerField()
    excel_sheet_name = models.CharField(max_length=100)
    submitted_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='submissions',
        on_delete=models.PROTECT,
        default='')
    curated = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class UnencodedSubmission(models.Model):
    """Define the data model to store submissions pending for encoding"""

    class Meta:
        db_table = 'unencoded_submission'

    submission_id = models.IntegerField(null=True)
    number_of_questions = models.IntegerField()
    excel_sheet_name = models.CharField(max_length=100)
    encoded = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class TranslatedQuestion(models.Model):
    """Define the data model to store translated questions"""

    class Meta:
        db_table = 'translated_question'

    question_id = models.ForeignKey(
        'Question',
        related_name='translations',
        on_delete=models.PROTECT,
        default='')
    question_text = models.CharField(max_length=1000)
    language = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
