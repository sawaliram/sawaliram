"""
Convert a locale name (eg. 'en') to a localised language name,
as per the settings (eg. 'English').
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

register = template.Library()

@register.filter
@stringfilter
def to_language_name(value):
    return dict(settings.LANGUAGES).get(value, value)
