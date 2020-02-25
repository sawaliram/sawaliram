from django.forms import ModelForm
from public_website.models import ContactUsSubmission

class ContactPageForm(ModelForm):
    class Meta:
        model = ContactUsSubmission
        exclude = ['created_on', 'updated_on']