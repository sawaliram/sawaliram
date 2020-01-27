from django.conf import settings

def language_list(request):
    language_dict = dict(settings.LANGUAGE_CHOICES)
    lang = request.session.get('lang', settings.DEFAULT_LANGUAGE)
    lang_label = language_dict.get(lang)

    # if it's an invalid choice, default to default language
    if lang_label is None:
        lang = settings.DEFAULT_LANGUAGE
        lang_label = language_dict.get(lang)

    return {
        'current_language': (lang, lang_label),
        'language_choices': settings.LANGUAGE_CHOICES,
        'current_path': request.get_full_path(),
    }
