"""Define the data models for all Sawaliram content"""

import datetime
from django.db import models
from django.conf import settings
from django.utils.http import urlencode

from django.utils.text import slugify
from django.utils.translation import get_language_info

from dashboard.mixins.draftables import (
    DraftableModel,
    PublishedDraftableManager,
    SubmittedDraftableManager,
    DraftDraftableManager,
)
from dashboard.mixins.translations import (
    TranslationMixin,
    translatable,
)
from django.urls import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)

LANGUAGE_CODES = {
    'english': 'en',
    'hindi': 'hi',
    'bengali': 'bn',
    'malayalam': 'ml',
    'marathi': 'mr',
    'tamil': 'ta',
    'telugu': 'te'
}


class Dataset(models.Model):
    """Define the data model for submitted datasets"""

    question_count = models.CharField(max_length=100)
    submitted_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='submitted_datasets',
        on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Dataset #{}'.format(self.id)


class QuestionArchive(models.Model):
    """Define the data model for raw submissions by volunteers"""

    class Meta:
        db_table = 'question_archive'

    school = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='', blank=True)
    student_name = models.CharField(max_length=100, blank=True)
    student_gender = models.CharField(max_length=100, default='', blank=True)
    student_class = models.CharField(max_length=100, default='', blank=True)
    question_text = models.CharField(max_length=1000, blank=True)
    question_text_english = models.CharField(max_length=1000, default='', blank=True)
    question_format = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    contributor = models.CharField(max_length=100, blank=True)
    contributor_role = models.CharField(max_length=100, blank=True)
    context = models.CharField(max_length=100, blank=True)
    medium_language = models.CharField(max_length=100, blank=True)
    curriculum_followed = models.CharField(max_length=100, default='', blank=True)
    published = models.BooleanField(default=False)
    published_source = models.CharField(max_length=200, default='', blank=True)
    published_date = models.DateField(default=datetime.date.today)
    question_asked_on = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=1000, default='')
    submitted_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='archived_questions',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    @property
    def en_text(self):
        if self.language in ('en', 'english'):
            return self.question_text
        else:
            return self.question_text_english

    def accept_question(self, acceptor):
        """
        Mark a question as approved, by the given acceptor (user).

        This basically changes a question from unmoderated to moderated
        by removing the QuestionArchive record and replacing it with
        a Question one.
        """

        q = Question()
        q.school = self.school
        q.area = self.area
        q.state = self.state
        q.student_name = self.student_name
        q.student_gender = self.student_gender
        q.student_class = self.student_class
        q.question_text = self.question_text
        q.question_text_english = self.question_text_english
        q.question_format = self.question_format
        q.language = self.language
        q.contributor = self.contributor
        q.contributor_role = self.contributor_role
        q.context = self.context
        q.medium_language = self.medium_language
        q.curriculum_followed = self.curriculum_followed
        q.published = self.published
        q.published_source = self.published_source
        q.published_date = self.published_date
        q.question_asked_on = self.question_asked_on
        q.notes = self.notes
        q.created_on = self.created_on
        q.updated_on = self.updated_on
        q.submitted_by = self.submitted_by
        q.curated_by = acceptor
        try:
            q.save()
            self.delete()
        except Exception as e:
            print('Error accepting question: %s' % e)

    def __str__(self):
        return 'Q{} (uncurated): {}'.format(self.id, self.question_text)


@translatable
class Question(models.Model):
    """Define the data model for questions curated by admins."""

    class Meta:
        db_table = 'question'

    translation_model = 'dashboard.PublishedTranslatedQuestion'
    translatable_fields = [
        'question_text',
        'school',
        'area',
        'state',
        'curriculum_followed',
    ]

    school = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='', blank=True)
    student_name = models.CharField(max_length=100, blank=True)
    student_gender = models.CharField(max_length=100, default='', blank=True)
    student_class = models.CharField(max_length=100, default='', blank=True)
    question_text = models.CharField(max_length=1000, blank=True)
    question_text_english = models.CharField(max_length=1000, default='', blank=True)
    question_format = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    contributor = models.CharField(max_length=100, blank=True)
    context = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=200, blank=True)
    contributor_role = models.CharField(max_length=100, blank=True)
    medium_language = models.CharField(max_length=100, blank=True)
    curriculum_followed = models.CharField(max_length=100, default='', blank=True)
    published = models.BooleanField(default=False)
    published_source = models.CharField(max_length=200, default='', blank=True)
    published_date = models.DateField(default=datetime.date.today)
    question_asked_on = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=1000, default='', blank=True)
    dataset_id = models.CharField(max_length=100, default='', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    curated_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='curated_questions',
        on_delete=models.CASCADE,
        default='')
    encoded_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='encoded_questions',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    # data members for encoding
    field_of_interest = models.CharField(max_length=100, default='', blank=True)
    subject_of_session = models.CharField(max_length=100, default='', blank=True)
    question_topic_relation = models.CharField(max_length=100, default='', blank=True)
    motivation = models.CharField(max_length=100, default='', blank=True)
    type_of_information = models.CharField(max_length=100, default='', blank=True)
    source = models.CharField(max_length=100, default='', blank=True)
    curiosity_index = models.CharField(max_length=100, default='', blank=True)
    urban_or_rural = models.CharField(max_length=100, default='', blank=True)
    type_of_school = models.CharField(max_length=100, default='', blank=True)
    comments_on_coding_rationale = models.CharField(max_length=500, default='', blank=True)

    def __str__(self):
        return 'Q{}: {}'.format(self.id, self.question_text)


@translatable
class Answer(models.Model):
    """Define the data model for answers in English"""

    translation_model = 'dashboard.PublishedAnswerTranslation'
    translatable_fields = ['answer_text']

    # Statuses

    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_PUBLISHED = 'published'

    class Meta:
        db_table = 'answer'

    answer_text = models.TextField()
    language = models.CharField(
        max_length=100,
        default='en')
    question_id = models.ForeignKey(
        'Question',
        related_name='answers',
        on_delete=models.PROTECT,
        default='')
    status = models.CharField(max_length=50, default='submitted')
    submitted_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='answers',
        on_delete=models.CASCADE,
        default='')
    approved_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='approved_answers',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    published_on = models.DateTimeField(blank=True, null=True)

    comments = GenericRelation('dashboard.Comment')

    def __str__(self):
        '''Return unicode representation of this Answer'''

        return 'Answer [{}]: {}'.format(
            self.question_id.language,
            self.question_id.question_text,
        )

    def get_absolute_url(self):
        if self.status == 'published':
            return reverse('public_website:view-answer', kwargs={
                'question_id': self.question_id.id,
                'answer_id': self.id,
            })
        else:
            return reverse('dashboard:review-answer',kwargs={
                'question_id': self.question_id.id,
                'answer_id': self.id,
            })

    @property
    def author(self):
        return self.submitted_by

    def get_language_name(self):
        """
        Return the full language name
        """
        for language, code in LANGUAGE_CODES.items():
            if code == self.language:
                return language

class AnswerTranslation(DraftableModel, TranslationMixin):
    '''
    Stores translated data for a given Answer
    '''

    # Where we're translating from

    source = models.ForeignKey(
        'Answer',
        related_name='translations',
        on_delete=models.PROTECT,
        default='')

    # What we're translating

    answer_text = models.TextField()

    # Comments (for review process)

    comments = GenericRelation('dashboard.Comment')

    def get_absolute_url(self):
        '''
        Returns the edit page of the translation
        '''

        if self.is_published:
            return '?lang='.join([
                reverse(
                    'public_website:view-answer',
                    kwargs={
                        'question_id': self.source.question_id.id,
                        'answer_id': self.source.id,
                    }
                ),
                self.language
            ])
        elif self.is_submitted:
            return reverse(
                'dashboard:review-answer-translation',
                kwargs={
                    'pk': self.id,
                }
            )
        else:
            return reverse(
                'dashboard:edit-answer-translation',
                kwargs={
                    'answer': self.source.id,
                    'source': self.source.question_id.id,
                    'lang_from': self.source.language,
                    'lang_to': self.language,
                }
            )


    def get_delete_url(self):
        '''
        Generates the URL at which to delete an answer. Note that this
        currently points to the linked question; both are deleted at
        the same time.
        '''

        return reverse('dashboard:delete-answer-translation', kwargs={
            'pk': self.id
        })

    def __str__(self):
        return 'Q{}A{}T{} [{}->{}]: {}'.format(
            self.source.question_id.id,
            self.source.id,
            self.id,
            self.source.language,
            self.language,
            self.source.question_id.question_text,
        )
    def get_full_name(self): 
        return self.get_full_name

class DraftAnswerTranslation(
    AnswerTranslation.get_draft_model(),
    AnswerTranslation,
):
    objects = DraftDraftableManager()
    class Meta:
        proxy = True

class SubmittedAnswerTranslation(
    AnswerTranslation.get_submitted_model(),
    AnswerTranslation,
):
    objects = SubmittedDraftableManager()
    class Meta:
        proxy = True

    def get_publish_url(self):
        return reverse(
            'dashboard:publish-answer-translation',
            kwargs={
                'pk': self.id,
            }
        )

class PublishedAnswerTranslation(
    AnswerTranslation.get_published_model(),
    AnswerTranslation,
):
    objects = PublishedDraftableManager()
    class Meta:
        proxy = True


class AnswerCredit(models.Model):
    """Define the data model for answer credits"""

    class Meta:
        db_table = 'answer_credit'
        ordering = ['credit_title_order']

    credit_title = models.CharField(max_length=50)
    credit_title_order = models.IntegerField(default=0)
    credit_user_name = models.CharField(max_length=100)
    is_user = models.BooleanField(default=False)
    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='answer_credits',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    answer = models.ForeignKey(
        'Answer',
        related_name='credits',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        credit_sorting_order = {
            'author': 1,
            'co-author': 2,
            'publication': 3,
            'submitter': 4
        }
        self.credit_title_order = credit_sorting_order[self.credit_title]
        super(AnswerCredit, self).save(*args, **kwargs)



class AnswerTranslationCredit(models.Model):
    """Define the data model for answer translation credits"""

    class Meta:
        db_table = 'answer_translation_credit'
        ordering = ['credit_title_order']

    credit_title = models.CharField(max_length=50)
    credit_title_order = models.IntegerField(default=0)
    credit_user_name = models.CharField(max_length=100)
    is_user = models.BooleanField(default=False)
    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='answer_translation_credits',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    answer = models.ForeignKey(
        'AnswerTranslation',
        related_name='translation_credits',
        on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        credit_sorting_order = {
            'translator-author': 1,
            'translator-co-author': 2,
            'translator-submitter': 3
        }
        self.credit_title_order = credit_sorting_order[self.credit_title]
        super(AnswerTranslationCredit, self).save(*args, **kwargs)



class ArticleCredit(models.Model):
    """Define the data model for article credits"""

    class Meta:
        db_table = 'article_credit'
        ordering = ['credit_title_order']

    credit_title = models.CharField(max_length=50)
    credit_title_order = models.IntegerField(default=0)
    credit_user_name = models.CharField(max_length=100)
    is_user = models.BooleanField(default=False)
    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='article_credits',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    article = models.ForeignKey(
        'Article',
        related_name='credits',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        credit_sorting_order = {
            'author': 1,
            'co-author': 2,
            'publication': 3,
            'submitter': 4
        }
        self.credit_title_order = credit_sorting_order[self.credit_title]
        super(ArticleCredit, self).save(*args, **kwargs)



class ArticleTranslationCredit(models.Model):
    """Define the data model for article translation credits"""

    class Meta:
        db_table = 'article_translation_credit'
        ordering = ['credit_title_order']

    credit_title = models.CharField(max_length=50)
    credit_title_order = models.IntegerField(default=0)
    credit_user_name = models.CharField(max_length=100)
    is_user = models.BooleanField(default=False)
    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='article_translation_credits',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    article = models.ForeignKey(
        'ArticleTranslation',
        related_name='translation_credits',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        credit_sorting_order = {
            'translator-author': 1,
            'translator-co-author': 2,
            'translator-submitter': 3
        }
        self.credit_title_order = credit_sorting_order[self.credit_title]
        super(ArticleTranslationCredit, self).save(*args, **kwargs)


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
        on_delete=models.CASCADE,
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


class TranslatedQuestion(DraftableModel, TranslationMixin):
    """Define the data model to store translated questions"""

    class Meta:
        db_table = 'translated_question'

    # Where we're translating from

    source = models.ForeignKey(
        'Question',
        related_name='translations',
        on_delete=models.PROTECT,
        default='')

    # What we're translating

    question_text = models.CharField(max_length=1000, blank=True)
    school = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='', blank=True)
    curriculum_followed = models.CharField(
        max_length=100,
        default='',
        blank=True)

    def __str__(self):
        return 'Q{}T{} [{}->{}]: {}'.format(
            self.source.id,
            self.id,
            self.source.language,
            self.language,
            self.question_text or self.source.question_text,
        )

    def get_absolute_url(self):
        # TODO: create a view for questions and redirect to that
        return '/'

class DraftTranslatedQuestion(
    TranslatedQuestion.get_draft_model(),
    TranslatedQuestion,
):
    objects = DraftDraftableManager()
    class Meta:
        proxy = True

class SubmittedTranslatedQuestion(
    TranslatedQuestion.get_submitted_model(),
    TranslatedQuestion,
):
    objects = SubmittedDraftableManager()
    class Meta:
        proxy = True

class PublishedTranslatedQuestion(
    TranslatedQuestion.get_published_model(),
    TranslatedQuestion,
):
    objects = PublishedDraftableManager()
    class Meta:
        proxy = True


@translatable
class Article(DraftableModel):
    '''
    Complete data model holding all kinds of articles. This includes:
      * ArticleDraft
      * SubmittedArticle
      * Article

    This is internally tracked via the 'status' parameter. You can
    also query articles with the specified status by using its proxy
    model (which internally checks the 'status' parameter before
    returning results).
    '''

    translation_model = 'dashboard.PublishedArticleTranslation'
    translatable_fields = ['title', 'body']

    title = models.CharField(max_length=1000, null=True)
    language = models.CharField(max_length=100,
        choices=settings.CONTENT_LANGUAGES,
        default='en')
    author = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='articles',
        on_delete=models.CASCADE,
        default='',
        null=True)

    body = models.TextField(null=True)

    cover_image = models.CharField(
        max_length=100,
        default='',
        blank=True,
        null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    approved_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='approved_articles',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)

    comments = GenericRelation('dashboard.Comment')

    class Meta:
        db_table = 'articles'

    def get_slug(self):
        return slugify(self.title)

    def __str__(self):
        return 'Article #{}: {}'.format(self.id, self.title)

    def get_absolute_url(self):
        if self.is_draft:
            return reverse('dashboard:edit-article', kwargs={
                'draft_id': self.id,
            })
        elif self.is_submitted:
            return reverse('dashboard:review-article', kwargs={
                'article': self.id,
            })
        else:
            return reverse('public_website:view-article', kwargs={
                'article': self.id,
            })

class ArticleDraft(Article.get_draft_model(), Article):
    objects = DraftDraftableManager()
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('dashboard:edit-article', kwargs={
            'draft_id': self.id
        })

class SubmittedArticle(Article.get_submitted_model(), Article):
    objects = SubmittedDraftableManager()
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('dashboard:review-article', kwargs={
            'article': self.id
        })

class PublishedArticle(Article.get_published_model(), Article):
    objects = PublishedDraftableManager()
    class Meta:
        proxy = True

class Comment(models.Model):
    '''
    Generic class for comments on any kind of model 🎉
    '''

    # Main field
    text = models.TextField()

    # Metadata fields
    author = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='comments',
        on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # The following fields are used for defining 'target'
    content_type = models.ForeignKey(ContentType,
        on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    # And this is the aforementioned 'target', now defined
    target = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return 'Comment #{} by {} on {}'.format(
            self.id,
            self.author,
            self.target
        )

    def get_absolute_url(self):
        return self.target.get_absolute_url()
    
    def __str__(self): 
        return self.get_full_name()

class ArticleTranslation(DraftableModel, TranslationMixin):
    '''
    Stores translated data for a given article
    '''

    # What we're translating
    source = models.ForeignKey(
        'Article',
        related_name='translations',
        on_delete=models.CASCADE)

    # Translated Fields

    title = models.CharField(max_length=1000, null=True)
    body = models.TextField(null=True)

    # Comments (for review process)

    comments = GenericRelation('dashboard.Comment')

    def __str__(self):
        return 'B{}T{} [{}->{}]: {}'.format(
            self.source.id,
            self.id,
            self.source.language,
            self.language,
            self.title or self.source.title,
        )

    def get_absolute_url(self):
        '''
        Returns the default page of the translation, depending on
        publish status
        '''

        if self.is_published:
            return '?lang='.join([
                reverse(
                    'public_website:view-article',
                    kwargs={
                        'article': self.source.id,
                    }
                ),
                self.language,
            ])
        elif self.is_submitted:
            return reverse(
                'dashboard:review-article-translation',
                kwargs={
                    'pk': self.id,
                }
            )
        else:
            return reverse(
                'dashboard:edit-article-translation',
                kwargs={
                    'source': self.source.id,
                    'lang_from': self.source.language,
                    'lang_to': self.language,
                }
            )

    def get_edit_url(self):
        '''
        Returns the edit URL of a translation, depending on publish
        status. Published pieces will have no edit URL.
        '''

        if self.is_draft:
            return reverse(
                'dashboard:edit-article-translation',
                kwargs={
                    'source': self.source.id,
                    'lang_from': self.source.language,
                    'lang_to': self.language,
                }
            )
        elif self.is_submitted:
            return reverse(
                'dashboard:edit-submitted-article-translation',
                kwargs={
                    'pk': self.id
                }
            )
        else:
            return # don't return anything :P

    def get_delete_url(self):
        return reverse('dashboard:delete-article-translation', kwargs={
            'pk': self.id
        })

class DraftArticleTranslation(
    ArticleTranslation.get_draft_model(),
    ArticleTranslation
):
    objects = DraftDraftableManager()
    class Meta:
        proxy = True

class SubmittedArticleTranslation(
    ArticleTranslation.get_submitted_model(),
    ArticleTranslation,
):
    objects = SubmittedDraftableManager()
    class Meta:
        proxy = True

    def get_publish_url(self):
        return reverse(
            'dashboard:publish-article-translation',
            kwargs={
                'pk': self.id,
            }
        )

class PublishedArticleTranslation(
    ArticleTranslation.get_published_model(),
    ArticleTranslation
):
    objects = PublishedDraftableManager()
    class Meta:
        proxy = True
