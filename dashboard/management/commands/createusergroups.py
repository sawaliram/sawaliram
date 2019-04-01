"""
Create user groups and set permissions
"""
from django.core.management import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Creates user groups and sets group permissions"

    def handle(self, *args, **options):
        volunteers = Group.objects.get_or_create(name='volunteers')
        editors = Group.objects.get_or_create(name='editors')
        experts = Group.objects.get_or_create(name='experts')
        admins = Group.objects.get_or_create(name='admins')
