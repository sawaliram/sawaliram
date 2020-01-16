from django.db import models
from django.conf import settings

class TranslationMixin(models.Model):
    '''
    Mixin for storing data of something that needs to be translated
    '''

    class Meta:
        abstract = True

    language = models.CharField(max_length=100,
        choices=settings.LANGUAGE_CHOICES,
        default='en')

    translated_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='%(class)s',
        on_delete=models.PROTECT)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def translator(self):
        return self.translated_by
