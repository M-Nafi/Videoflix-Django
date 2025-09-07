from django.shortcuts import redirect

def redirect_to_admin(request):
    """
    Redirects the user to the Django admin interface.
    """
    return redirect('admin:index')

def redirect_to_schema(request):
    """
    Redirects the user to the API schema page.
    """
    return redirect('swagger-ui')

