"""
Update the contributor role value with new values.
Copy existing value to Notes column.
"""
from django.core.management import BaseCommand
from dashboard.models import Question


class Command(BaseCommand):
    help = "Update the contributor role value with new values"

    def handle(self, *args, **options):
        contributor_role_mapping = {
            'Academic Field Support Person': 'Project staff',
            'Project officer, TISS': 'Project staff',
            'Scientific Officer, Project Assistant, HBCSE': 'Project staff',
            'Scientific Officer, Project Assistant': 'Project staff',
            'Web Team Eklavya - Bhopal': 'Project staff',
            'Web Team Eklavya - Bhopal (Translation support by Amik Raj, CMI Chennai)': 'Project staff',
            'Web Team Eklavya - Bhopal; Hindi to English translation by Rajeshwari Nair (CMI)': 'Project staff',
            'Correspondent': 'Principal / Mentor',
            'Science teacher and correspondent': 'Principal / Mentor',
            'Principal': 'Principal / Mentor',
            'Volunteer with TNSF': 'Principal / Mentor',
            'Educator': 'Teacher',
            'Teacher': 'Teacher',
            'Maths Teacher': 'Teacher',
            'Science Teacher': 'Teacher',
            'Teacher in Andaman with Govt School; SRF at TIFRH': 'Teacher',
            'Outreach Volunteer; Science Education group at TIFRH': 'Volunteer',
            'School outreach volunteers for TCIS': 'Volunteer',
            'Volunteer': 'Volunteer',
            'Volunteer, Tamil Nadu Science Forum (Sci-Edu Group, TIFRH)': 'Volunteer',
            'Conducted Summer camp; VSRP with SciEdu group - Summer 2019': 'Researcher',
            'Sci Edu group, TIFRH': 'Researcher',
            'Science Education Group': 'Researcher',
            'Senior Research Fellow, Science Education group, TIFR Hyderabad': 'Researcher',
            'TIFRH School outreach volunteers (Sci-Education group)': 'Researcher',
            'Summer Intern at TIFRH': 'Researcher'
        }
        questions = Question.objects.all()

        for question in questions:
            if question.contributor_role in contributor_role_mapping:
                if question.notes == '':
                    question.notes = 'contributor_role: ' + question.contributor_role
                else:
                    question.notes += ';contributor_role: ' + question.contributor_role
                question.contributor_role = contributor_role_mapping[question.contributor_role]
                question.save()
