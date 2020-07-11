"""Define all data models for creating and managing users"""

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    """Define the manager to handle user creation"""

    def create_user(self, first_name, last_name, organisation, email, password):
        """
        Creates and saves a User with email and organisation
        """
        if not email:
            raise ValueError("Email must be provided to create a user")
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.organisation = organisation
        user.save()
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a user as superuser
        """
        email = self.normalize_email(email)
        user = self.create_user('Super', 'User', 'Sawaliram', email, password)
        user.is_staff()
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Define the data model for user"""

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    organisation = models.CharField(max_length=200, default='')
    organisation_role = models.CharField(max_length=50, null=True, blank=True)
    intro_text = models.CharField(max_length=300, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_short_name(self):
        """
        Return the first_name of the user
        """
        return self.first_name

    def get_full_name(self):
        """
        Return the full name of the user
        """
        return self.first_name + ' ' + self.last_name

    def is_staff(self):
        """
        Return whether the user is allowed access to the admin interface
        """
        return self.is_superuser


class Profile(models.Model):
    """Define the data model for user profile"""

    class Meta:
        db_table = 'user_profile'

    profile_picture = models.CharField(max_length=100, null=True)
    verification_code = models.TextField(null=True)
    verification_code_expiry = models.DateTimeField(null=True)
    password_reset_code = models.TextField(null=True)
    password_reset_code_expiry = models.DateTimeField(null=True)
    email_verified = models.BooleanField(default=False)
    user = models.OneToOneField(
        'sawaliram_auth.User',
        related_name='profile',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class VolunteerRequest(models.Model):
    """Define the data model for a volunteer request by a user"""

    class Meta:
        db_table = 'volunteer_request'

    permission_requested = models.CharField(max_length=50)
    request_text = models.TextField(null=True)
    status = models.CharField(max_length=50, default='pending')
    requested_by = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='volunteer_requests',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Bookmark(models.Model):
    """Define the model for bookmarks saved by users"""

    class Meta:
        db_table = 'bookmarks'

    content_type = models.CharField(max_length=50)
    question = models.ForeignKey(
        'dashboard.Question',
        related_name='bookmarks',
        on_delete=models.CASCADE,
        default='',
        blank=True,
        null=True)
    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='bookmarks',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    """Define the model for user notifications"""

    class Meta:
        db_table = 'notifications'

    notification_type = models.CharField(max_length=50)
    title_text = models.CharField(max_length=50)
    description_text = models.CharField(max_length=500)
    target_url = models.CharField(max_length=50)
    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='notifications',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
