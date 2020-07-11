import warnings

from django.db import models
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

class TranslationMixin(models.Model):
    '''
    Mixin for storing data of something that is a translation for
    something else (such as an ArticleTranslation of an Article).
    '''

    class Meta:
        abstract = True

    language = models.CharField(max_length=100,
        choices=settings.LANGUAGE_CHOICES,
        default='en')

    translated_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='%(class)s',
        on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def translator(self):
        return self.translated_by

def translatable(cls):
    '''
    Takes a model and makes it translatable by setting values and
    properties. This means you can:

      * Set the model language using set_language: this fetches the
        translation if possible and falls back to the default language
        otherwise.
      * Access translated properties using the tr_PROPERTY parameters,
        eg. `tr_title` for the translated title.
      * Generate the list of languages in which a translation is
        available using the get_available_languages function.

    To enable these features, you will have to use this function as a
    decorator on your class, and also ensure your class has the
    following properties set:

      * translation_model = a `django.models.Model` class that holds
        the translated data (ideally, but not required to, inherit
        from TranslatableMixin).
      * translatable_fields = the list of fields (`django.models.Field`)
        that should be treated as "translatable". It is expected that
        these fields, with identical names, will also be present on the
        translation_model specified above.
      * language = a field (`django.models.Field`), ideally a
        `CharField`, that is used to specify the language of the current
        object.

    Sample usage:

        @translation
        class Article(models.Model):
            translation_model = 'TranslatedArticle'
            translatable_fields = ['title', 'body']

            language = models.CharField(max_length=6)
            title = models.CharField(max_length=512)
            body = models.TextField()

        class ArticleTranslation(models.Model):
            language = models.CharField(max_length=6)
            source = models.ForeignKeyField(Article)
            translated_by = models.CharField(max_length=64)

            title = models.CharField(max_length=512)
            body = models.TextField()

    Sample usage would be as follows:

        >>> a = Article.create(
        ... language='en',
        ... title='Hello',
        ... body='...',
        ... )
        ...
        >>> t = ArticleTranslation.create(
        ... language='ka',
        ... title='ನಮಸ್ಕಾರ',
        ... body='...',
        ...)
        ...
        >>> a.title
        'hello'
        >>> a.tr_title # the translated version: not yet translated
        'hello'
        >>> # Update all tr_ properties to use new language version...
        >>> a.set_language('ka')
        >>> a.tr_title # now it's been translated
        'ನಮಸ್ಕಾರ'

    You can also run set_language() multiple times to keep changing
    the current display language of the model.
    '''

    # Check that all properties are set properly

    # Dummy property that gets filled by set_language():
    cls.translation = None

    # Test translation model
    if not hasattr(cls, 'translation_model'):
        raise ImproperlyConfigured(
            "Please specify a translations model using the 'tr_model' "
            "parameter on {}".format(cls.__name__)
        )

    if not hasattr(cls, 'translatable_fields'):
        warnings.warn((
                "No translatable fields specified on {}. "
                "This means you cannot use most translation features. "
                "Please set the 'translatable_fields' list if you want "
                "to make use of them."
            ).format(cls.__name__))
        cls.translatable_fields = []

    if not hasattr(cls, 'language'):
        raise ImproperlyConfigured((
            "{} has no 'language' model field! This field is required"
            "for all translation models to work correctly.")
            .format(cls.__name__))

    # Language handling

    def set_language(self, language):
        '''
        Fetches a translation in the specified language, if available,
        and caches it in self.translation for future use.

        This step is skipped if the main article is already in the
        current language or if not translation is available (in which
        case we'll fall back to providing the original version).

        In future, this could be updated to use a hierarchy of
        preferred languages, but we don't have time for that at the
        moment :P
        '''

        # If we're already the correct language, do nothing
        if language == self.language:
            return

        # search for translations with the given language
        t = apps.get_model(self.translation_model).objects.filter(
            source=self,
            language=language,
        )

        # if it's there, set that to the translation
        if t.count() > 0:
            # TODO: warn if more than one translation per language

            # set the result as a translation
            self.translation = t[0]

        # if it's not there, do nothing
        # we'll fall back to using our default values

    cls.set_language = set_language

    @property
    def translated_by(self):
        if self.translation:
            return self.translation.translated_by
        else:
            return None
    cls.translated_by = translated_by

    @property
    def tr_language(self):
        if self.translation and self.translation.language:
            return self.translation.language
        else:
            return self.language
    cls.tr_language = tr_language

    @property
    def is_translated(self):
        return self.translation is not None
    cls.is_translated = is_translated

    def list_available_languages(self):
        '''
        Generate a list of languages for which translations are
        currently available for this model, and return them as a list
        in the format (lang_code, lang_name). For example, if there are
        translations available in Bengali and Marathi, the output would
        be:

            [('bn', 'বাংলা'), ('mr', 'मराठी')]

        This list includes the language of the original object (as
        opposed to the language of a translation).
        '''
        langs = [self.language]
        langs += [
            t.language
            for t
            in self.translations.filter(
                status=(apps
                    .get_model(self.translation_model)
                    .STATUS_PUBLISHED),
            )
        ]

        langs_dedup = list(set(langs))
        langs_dedup.sort()

        languages = [
            (lang, dict(settings.CONTENT_LANGUAGES).get(lang, lang))
            for lang in langs_dedup
        ]

        return languages
    cls.list_available_languages = list_available_languages

    def make_tr(field):
        '''
        Makes a property which fetches its value from the translation
        model, if available, and from itself otherwise.

        For example, `make_tr('hello')` will return a property that
        returns `self.translation.hello` if the translation exists, and
        `self.hello` otherwise. Of course, we assume you do the sensible
        thing and actually define properties called 'hello' on your
        models before trying to access them.
        '''

        @property
        def tr_field(self):
            if self.translation:
                return getattr(self.translation, field)
            else:
                return getattr(self, field)

        return tr_field

    for field in cls.translatable_fields:
        setattr(cls, 'tr_{}'.format(field), make_tr(field))

    return cls
