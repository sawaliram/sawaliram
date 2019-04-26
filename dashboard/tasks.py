from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task

import logging

from django.core.cache import cache
from dashboard.models import (
    QuestionArchive,
    Question,
    User,
    Answer,
    UncuratedSubmission)

logger = logging.getLogger(__name__)

def get_user_request_count():
    return 0  # TODO: actually count something

def get_uncurated_submission_count():
    return UncuratedSubmission.objects.count()

def get_unreviewed_answer_count():
    return Answer.objects.filter(approved_by__isnull=False).distinct().count()

def get_unanswered_question_count():
    return Question.objects.filter(answers__isnull=False).distinct().count()

def get_untranslated_content_count():
    # TODO: count other things besides questions
    return QuestionArchive.objects.filter(question_text_english='').count()

def get_question_count():
    return Question.objects.count()

@periodic_task(run_every=(crontab(hour='*/1')),  # runs every hour
    name='update_counts',
    ignore_result=True)
def cacheThemAll():
    '''
    Calculate all object totals and add them to the appropriate slots
    in the cache
    '''
    
    logger.debug('Updating counts cache')

    cache.set('count.user.requests', get_user_request_count())
    cache.set('count.submission.uncurated', get_uncurated_submission_count())
    cache.set('count.answer.unreviewed', get_unreviewed_answer_count())
    cache.set('count.question.unanswered', get_unanswered_question_count())
    cache.set('count.content.untranslated', get_untranslated_content_count())
    cache.set('count.question', get_question_count())
