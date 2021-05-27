
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
