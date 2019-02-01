"""
Create user groups and set permissions
"""
from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from dashboard.models import User

class Command(BaseCommand):
    help="Creates user groups and sets group permissions"

    def handle(self, *args, **options):

        # groups
        volunteers = Group.objects.get_or_create(name='volunteers')
        moderators = Group.objects.get_or_create(name='moderators')
        experts = Group.objects.get_or_create(name='experts')
        admins = Group.objects.get_or_create(name='admins')
