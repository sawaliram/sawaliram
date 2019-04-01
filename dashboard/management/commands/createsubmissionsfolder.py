"""
Create assets/submission dir to save submitted datasets
"""
from django.core.management import BaseCommand
import os


class Command(BaseCommand):
    help = "Creates assets/submission dir to save submitted datasets"

    def handle(self, *args, **options):
        path_to_submissions_dir = os.path.join(
            os.path.dirname(__file__), '../../../assets') + '/submissions'

        if not os.path.exists(path_to_submissions_dir):
            os.makedirs(path_to_submissions_dir)
