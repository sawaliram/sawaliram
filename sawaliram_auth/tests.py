from django.test import TestCase
from sawaliram_auth.models import *

class CreateSuperUserTest(TestCase):
    '''
    Checks that superusers can be created without a hitch
    '''

    def test_create_superuser(self):
        '''
        Verify that the create_superuser command is working properly
        '''

        u = User.objects.create_superuser('crow@sawaliram.org', 'pass')
        u.save()

        assert u.is_superuser
