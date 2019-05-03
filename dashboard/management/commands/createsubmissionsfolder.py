"""
Create assets/submission/ dirs to save submitted datasets
"""
from django.core.management import BaseCommand
import os


class Command(BaseCommand):
    help = "Creates assets/submission dir to save submitted datasets"

    def handle(self, *args, **options):
        path_to_uncurated_submissions_dir = os.path.join(
            os.path.dirname(__file__), '../../../assets')
        + '/submissions/uncurated'

        path_to_unencoded_submissions_dir = os.path.join(
            os.path.dirname(__file__), '../../../assets')
        + '/submissions/unencoded'

        if not os.path.exists(path_to_uncurated_submissions_dir):
            os.makedirs(path_to_uncurated_submissions_dir)

        if not os.path.exists(path_to_unencoded_submissions_dir):
            os.makedirs(path_to_unencoded_submissions_dir)
