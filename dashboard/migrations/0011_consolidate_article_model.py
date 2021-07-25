# Generated by Django 2.2.4 on 2020-01-08 05:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20191216_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittedarticle',
            name='author',
        ),
        migrations.RemoveField(
            model_name='translatedarticle',
            name='author',
        ),
        migrations.RemoveField(
            model_name='translatedarticle',
            name='original_article',
        ),
        migrations.AlterModelManagers(
            name='article',
            managers=[
                ('get_published', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='articles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='articlecomment',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='dashboard.Article'),
        ),
        migrations.DeleteModel(
            name='ArticleDraft',
        ),
        migrations.DeleteModel(
            name='SubmittedArticle',
        ),
        migrations.DeleteModel(
            name='TranslatedArticle',
        ),
    ]
