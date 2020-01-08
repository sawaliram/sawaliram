# Generated by Django 2.2.3 on 2019-08-28 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0002_auto_20190812_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerDraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField()),
                ('last_saved', models.DateTimeField(auto_now=True)),
                ('answered_by', models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='draft_answers', to=settings.AUTH_USER_MODEL)),
                ('question_id', models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='draft_answers', to='dashboard.Question')),
            ],
            options={
                'db_table': 'answer_draft',
            },
        ),
    ]
