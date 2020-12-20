from django.contrib import admin

from .models import (
    User,
    Profile,
)

class AnswerCreditInline(admin.StackedInline):
    model = Profile
    view_on_site = False
    show_change_link = True

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        'email',
        'get_full_name',
        'is_active',
        'created_on',
    ]

    search_fields = [
        'email',
        'first_name',
        'last_name',
    ]

    list_filter = [
        'created_on',
        'updated_on',
    ]

    inlines = [
        AnswerCreditInline,
    ]
