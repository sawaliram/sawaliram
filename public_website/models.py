from django.db import models


class AnswerUserComment(models.Model):
    """Define the data model for user comments on Answers"""

    class Meta:
        db_table = 'answer_user_comment'

    text = models.TextField()

    answer = models.ForeignKey(
        'dashboard.Answer',
        related_name='user_comments',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='answer_user_comments',
        on_delete=models.PROTECT)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class ContactUsSubmission(models.Model):
    """Defines models for contact us page submissions by users"""
    
    fullname = models.CharField(max_length=100)
    emailid = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)