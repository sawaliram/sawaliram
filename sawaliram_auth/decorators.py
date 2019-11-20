
from django.shortcuts import redirect
from functools import wraps


def volunteer_permission_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name='volunteers').exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('sawaliram_auth:how_can_i_help')

        return function(request, *args, **kwargs)

    return wrap
