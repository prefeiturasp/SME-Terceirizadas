
def has_perm(function):
    def wrap(request, *args, **kwargs):

        request.

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__nam__

    return wrap
