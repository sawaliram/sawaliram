import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import csv

from celery import shared_task
from django.core.cache import cache
from sawaliram_auth.models import (
    User,
    VolunteerRequest
)
from dashboard.models import (
    Dataset,
    SubmittedArticle,
    PublishedArticle,
    Question,
    Answer
)


@shared_task
def updateDashboardTasksStats():
    """
    Calculate all displayed task statistics and set them in the cache
    """

    cache.set('total_users', User.objects.count())
    cache.set('pending_access_requests', VolunteerRequest.objects.filter(status='pending').count())
    cache.set('new_datasets', Dataset.objects.filter(status='new').count())
    cache.set('submitted_articles', SubmittedArticle.objects.count())
    cache.set('unanswered_questions', Question.objects.exclude(answers__status='published').count())
    cache.set('unreviewed_answers', Answer.objects.filter(status='submitted').count())
    cache.set('total_questions', Question.objects.count())
    cache.set('published_articles', PublishedArticle.objects.count())
    cache.set(
        'items_to_translate',
        Question.objects.count() +
        Answer.objects.filter(status='submitted').count() +
        PublishedArticle.objects.count()
    )

def update_local_csv(objects, fields, csv_file_name):
    """
    Writes the rows of all the objects in csv_file_name file
    """
    with open(csv_file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write your header first
        header = []
        for i in range(len(fields)):
            field = fields[i]
            header.append(str(field))
        writer.writerow(header)

        for obj in objects:
            row = []
            for field in fields:
                 row.append(str(obj[field]))
            writer.writerow(row)


def update_sheet(spreadsheet, csv_file_name):
    """
    Updates the google sheet "sheet" with the data from the file csv_file_name
    """
    with open(csv_file_name, 'r') as file_ob:
        content = file_ob.read()
        client.import_csv(spreadsheet.id, data=content)




@shared_task
def update_to_cloud_task():
    scope = ['https://spreadsheets.google.com/feeds',"https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.environ.get('google_secret_key_file'), scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("questions")
    fields = ['state', 'student_gender', 'student_class', 'question_format', 'contributor_role', 'context', 'medium_language', 'curriculum_followed', 'question_asked_on', 'field_of_interest', 'language']
    csv_file_name = "question_tableau.csv"
    objects = Question.objects.values(*fields)
    update_local_csv(objects, fields, csv_file_name)
    update_sheet(spreadsheet, csv_file_name)
