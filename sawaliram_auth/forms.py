"""Define the forms for authenticating users"""

from django import forms

from sawaliram_auth.models import User


class SignInForm(forms.Form):

    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        label=''
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label='')


class SignUpForm(forms.Form):

    def check_email_availability(email):
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email address already in use!', code='email_exists')

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'First Name'}),
        label=''
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Last Name'}),
        label=''
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        validators=[check_email_availability],
        label=''
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'password-field'}),
        label='')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return first_name.capitalize()

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name.capitalize()
