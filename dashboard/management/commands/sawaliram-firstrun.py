from django.core.management import BaseCommand, call_command

from sawaliram_auth.models import User

class Command(BaseCommand):
    help = 'Run all initial setup scripts for Sawaliram'

    def handle(self, *args, **options):
        print('Run createsubmissionsfolder')
        call_command('createsubmissionsfolder')

        print('Run createusergroups')
        call_command('createusergroups')

        # Check for superuser
        if not User.objects.filter(is_superuser=True).count():
            # No superusers. Offer to create one.
            print(
                'No superuser account was found in your database.'
                ' Would you like to create one now? [Y/n]',
                end=' '
            )
            i = input()

            if (not i) or (i[0].lower() != 'n'):
                call_command('createsuperuser')
            else:
                print("Skipping superuser creation (you didn't want it).")
        else:
            print('Skipping superuser creation (already exists).')
        print(
            'All set up!',
            'You can now begin using your new Sawaliram installation :)',
        )
