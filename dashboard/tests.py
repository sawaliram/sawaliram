from django.test import TestCase
from dashboard.models import *
from sawaliram_auth.models import User
class ArticleTranslationTests(TestCase):
    '''
    Check translations functionality of Articles, Questions and Answers.
    '''

    # Test data
    title_en = 'Grimnismal'
    title_is = 'Grímnismál'
    body_en = 'For one drink you shall never get a better reward!'
    body_is = 'Eins drykkjar þú skalt aldrigi betri gjöld geta'

    def setUp(self):
        u1 = User.objects.create_user(
            first_name='Hugin',
            last_name='Hrafna',
            organisation='Familiars of Odin',
            email='hugin@hrafnaguo.god',
            password='pass',
        )

        u2 = User.objects.create_user(
            first_name='Munin',
            last_name='Hrafna',
            organisation='Familiars of Odin',
            email='munin@hrafnaguo.god',
            password='pass',
        )

        a = PublishedArticle.objects.create(
            id=1,
            title=self.title_en,
            body=self.body_en,
            language='en',
            author=u1,
            approved_by = u2,
        )

        t = PublishedArticleTranslation.objects.create(
            source=a,
            language='is',
            title=self.title_is,
            body=self.body_is,
            translated_by=u1,
        )

    def test_article_tr_values(self):
        '''
        Check that tr_ values (tr_title, etc.) are working properly
        on normal (untranslated) model
        '''

        a = Article.objects.get(id=1)
        self.assertEqual(a.tr_title, self.title_en)
        self.assertEqual(a.tr_body, self.body_en)

    def test_article_tr_fallback(self):
        '''
        Checks that tr_ values remain with fallback original-language
        value when a translation is not available
        '''

        a = Article.objects.get(id=1)
        a.set_language('ta')
        self.assertEqual(a.tr_title, self.title_en)
        self.assertEqual(a.tr_body, self.body_en)

    def test_article_tr_newlanguage(self):
        '''
        Checks that translated tr_ values are available when a
        translation is available
        '''

        a = Article.objects.get(id=1)
        a.set_language('is')
        self.assertEqual(a.tr_title, self.title_is)
        self.assertEqual(a.tr_body, self.body_is)

class QuestionTranslationTestCase(TestCase):
    '''
    Check that Questions and Answers are translatable
    '''

    question_en = "How does the moon always show a single face to us?"
    question_bn = "চাঁদ কীভাবে আমাদের একটা দিকই দেখায়?"
    answer_en = "Tidal locking"
    answer_bn = "জোয়ার ব্যবস্থাপনা"

    def setUp(self):
        u1 = User.objects.create_user(
            first_name='Hugin',
            last_name='Hrafna',
            organisation='Familiars of Odin',
            email='hugin@hrafnaguo.god',
            password='pass',
        )

        u2 = User.objects.create_user(
            first_name='Munin',
            last_name='Hrafna',
            organisation='Familiars of Odin',
            email='munin@hrafnaguo.god',
            password='pass',
        )

        q1 = Question.objects.create(
            id=1,
            question_text=self.question_bn,
            question_text_english=self.question_en,
            language="bn",
            curated_by=u1,
            encoded_by=u2,
        )

        t1 = TranslatedQuestion.objects.create(
            source=q1,
            language='en',
            question_text=self.question_en,
            translated_by=u2,
            status=TranslatedQuestion.STATUS_PUBLISHED,
        )

        a = Answer.objects.create(
            id=1,
            question_id=q1,
            answer_text=self.answer_en,
            language='en',
            status='submitted',
            submitted_by=u1,
        )

        t2 = AnswerTranslation.objects.create(
            source=a,
            language='bn',
            answer_text=self.answer_bn,
            translated_by=u2,
            status=AnswerTranslation.STATUS_PUBLISHED,
        )

    def test_question_tr_values(self):
        q = Question.objects.get(id=1)
        self.assertEqual(q.tr_question_text, self.question_bn)
        # TODO: test school, area, state, curriculum_followed

    def test_question_tr_fallback(self):
        q = Question.objects.get(id=1)
        q.set_language('te')
        self.assertEqual(q.tr_question_text, self.question_bn)

    def test_question_tr_newlanguage(self):
        q = Question.objects.get(id=1)
        q.set_language('en')
        self.assertEqual(q.tr_question_text, self.question_en)

    def test_question_list_available_languages(self):
        '''
        Does the question correctly list all available languages?
        '''

        q = Question.objects.get(id=1)
        self.assertEqual(
            set(dict(q.list_available_languages())),
            set(('en', 'bn'))
        )

    def test_answer_tr_values(self):
        a = Answer.objects.get(id=1)
        self.assertEqual(a.tr_answer_text, self.answer_en)

    def answer_tr_fallback(self):
        a = Answer.objects.get(id=1)
        a.set_language('te')
        self.assertEqual(a.tr_answer_text, self.answer_en)

    def answer_tr_newlanguage(self):
        a = Answer.objects.get(id=1)
        a.set_language('bn')
        self.assertEqual(a.tr_answer_text, self.answer_bn)

    def test_answer_list_available_languages(self):
        '''
        Does the question correctly list all available languages?
        '''

        a = Answer.objects.get(id=1)
        self.assertEqual(
            set(dict(a.list_available_languages())),
            set(('en', 'bn'))
        )
