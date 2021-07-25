"""
Create user groups and set permissions
"""
from django.core.management import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Creates user groups and sets group permissions"

    def handle(self, *args, **options):
        users = Group.objects.get_or_create(name='users')
        volunteers = Group.objects.get_or_create(name='volunteers')
        reviewers = Group.objects.get_or_create(name='reviewers')
        experts = Group.objects.get_or_create(name='experts')
        admins = Group.objects.get_or_create(name='admins')
        writers = Group.objects.get_or_create(name='writers')
        translators = Group.objects.get_or_create(name='translators')
