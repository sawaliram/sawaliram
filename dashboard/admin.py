from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext as _

from .models import (
    Question,
    Answer,
    Article,
    ArticleTranslation,
    AnswerTranslation,
    TranslatedQuestion,
    AnswerCredit,
    ArticleCredit
)


def make_bulk_updater(field_name):
    def _bulk_update(modeladmin, request, queryset):
        ct = ContentType.objects.get_for_model(queryset.model)
        selected = queryset.values_list('pk', flat=True)

        return redirect('?'.join([
            reverse('dashboard:admin-bulk-update-field'),
            urlencode({
                'field': field_name,
                'ids': ','.join(str(pk) for pk in selected),
                'ct': ct.pk,
            }),
        ]))
    _bulk_update.short_description = _('Update %s') % field_name

    return _bulk_update


def publish_status(obj):
    '''
    Displays the published status of a particular object
    '''

    if obj.is_published:
        return 'published'
    elif obj.is_submitted:
        return 'submitted'
    elif obj.is_draft:
        return 'draft'
    else:
        return 'UNKNOWN: error?'

publish_status.short_description = 'Publish Status'


class AnswerCreditInline(admin.TabularInline):
    model = AnswerCredit
    view_on_site = False
    show_change_link = True


class ArticleCreditInline(admin.TabularInline):
    model = ArticleCredit
    view_on_site = False
    show_change_link = True


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    def question_text_english(obj):
        return (obj.question_id.question_text_english
            or obj.question_id.question_text)
    question_text_english.short_description = 'Question (en)'
    list_display = [
        'question_id',
        question_text_english,
        'status',
        'submitted_by',
        'created_on',
        'updated_on',
    ]
    fields = [
        'question_id',
        'language',
        'answer_text',
        'status',
        'submitted_by',
        'approved_by',
    ]
    search_fields = ['question_id__id', 'question_id__question_text']
    inlines = [
        AnswerCreditInline,
    ]
    date_hierarchy = 'created_on'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['id', 'question_text', 'question_text_english']
    list_filter = [
        'language',
        'state',
        'field_of_interest',
        'student_gender',
        'context',
        'contributor_role',
        'student_class',
        'curriculum_followed',
        'medium_language',
    ]
    list_display = ['id', 'question_text', 'question_text_english', 'field_of_interest', 'area', 'state']

    actions = [
        'change_foi',
        'change_language',
        'change_state',
        'change_area',
        'change_moi',
        'change_class',
        'change_curriculum_followed',
        'change_context',
        'change_contributor_role',
    ]
    change_foi = make_bulk_updater('field_of_interest')
    change_language = make_bulk_updater('language')
    change_state = make_bulk_updater('state')
    change_area = make_bulk_updater('change_area')
    change_moi = make_bulk_updater('medium_language')
    change_class = make_bulk_updater('student_class')
    change_curriculum_followed = make_bulk_updater('curriculum_followed')
    change_context = make_bulk_updater('context')
    change_contributor_role = make_bulk_updater('contributor_role')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['title', 'body']
    list_filter = ['language', 'author']
    list_display = ['id', 'title', 'created_on', 'updated_on', 'published_on','author', publish_status]
    date_hierarchy = 'published_on'
    inlines = [
        ArticleCreditInline,
    ]


@admin.register(TranslatedQuestion)
class QuestionTranslationAdmin(admin.ModelAdmin):

    search_fields = ['source', 'question_text', 'school']
    list_filter = ['language', 'translated_by']
    list_display = [
        '__str__',
        'language',
        'translated_by',
        publish_status,
    ]
    date_hierarchy = 'created'


@admin.register(AnswerTranslation)
class AnswerTranslationAdmin(admin.ModelAdmin):
    search_fields = ['source', 'answer_text']
    list_filter = ['language', 'translated_by']
    list_display = [
        '__str__',
        'language',
        'translated_by',
        publish_status,
    ]
    date_hierarchy = 'created'

@admin.register(ArticleTranslation)
class ArticleTranslationAdmin(admin.ModelAdmin):
    search_fields = ['source', 'title', 'body']
    list_filter = ['language', 'translated_by']
    list_display = [
        '__str__',
        'language',
        'translated_by',
        publish_status,
    ]
    date_hierarchy = 'created'
