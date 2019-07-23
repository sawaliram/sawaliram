
from django.shortcuts import redirect


def volunteer_permission_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name='volunteers').exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('sawaliram_auth:how_can_i_help')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
