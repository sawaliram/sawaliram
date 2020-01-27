import warnings

from django.urls import reverse
from django.shortcuts import redirect
from django.utils.http import urlencode
from functools import wraps

def permission_required(group_name):
    '''
    Returns a decorator for authenticating based on group_name.

    Example: to only allow writers to access the view

    @permission_required('writers')
    def write_article(request):
        # ...
        return render(request, template, context)
    '''

    def _permission_required(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if request.user.groups.filter(name=group_name).exists():
                return function(request, *args, **kwargs)
            else:
                return redirect(''.join([
                    reverse('sawaliram_auth:how_can_i_help'),
                    '?',
                    urlencode({'next': request.get_full_path()}),
                ]))

            return function(request, *args, **kwargs)
        return wrap

    return _permission_required

def volunteer_permission_required(function):
    '''Deprecated: please use permission_required instead'''
    warnings.warn(
        '`volunteer_permission_required` is deprecated. '
        "Please use `permission_required('volunteer')` instead."
    )
    return permission_required('volunteers')(function)
