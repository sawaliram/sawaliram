# Generated by Django 2.2.13 on 2021-05-28 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sawaliram_auth', '0022_profile_profile_picture_bg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='title_text',
            field=models.CharField(max_length=80),
        ),
    ]
