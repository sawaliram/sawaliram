"""
Defines a custom filter to automatically add HTML-supported linebreaks
(<br />) to multiline plaintext
"""
from django import template

register = template.Library()

@register.filter(name='render_linebreaks')
def render_linebreaks(value):
    return value.replace('\n', '<br />\n')
