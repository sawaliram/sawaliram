"""Define the forms for authenticating users"""

from django import forms

from sawaliram_auth.models import User


class SignInForm(forms.Form):

    def check_if_email_exists(email):
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email address not found', code='email_not_found'
            )

    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        validators=[check_if_email_exists],
        label=''
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label='')


class ResetPasswordForm(forms.Form):

    def check_if_email_exists(email):
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email address not found', code='email_not_found'
            )

    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Registered Email',
            'class': 'registered-email'
        }),
        validators=[check_if_email_exists],
        label=''
    )


class ChangePasswordForm(forms.Form):

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password'}),
        label='')
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password'}),
        label='')

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data['new_password']
        confirm_new_password = self.cleaned_data['confirm_new_password']

        if not confirm_new_password:
            raise forms.ValidationError('You must confirm your password')
        if new_password != confirm_new_password:
            raise forms.ValidationError('Your passwords do not match')


class SignUpForm(forms.Form):

    def check_email_availability(email):
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email address already in use!', code='email_exists'
            )

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'First Name'}),
        label=''
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Last Name'}),
        label=''
    )
    organisation = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Organisation',
        'list': 'organisationChoices'}),
        label='',)
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
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password'}),
        label='')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return first_name.capitalize()

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name.capitalize()

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if not confirm_password:
            raise forms.ValidationError('You must confirm your password')
        if password != confirm_password:
            raise forms.ValidationError('Your passwords do not match')
