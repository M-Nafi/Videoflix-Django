from django.shortcuts import redirect


def redirect_to_api(request):
    """
    Redirect to API documentation or admin interface.
    """
    return redirect('/admin/')