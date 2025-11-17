# decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login to access this page")
                return redirect('adminlogin')
            
            # Check permission for ALL users (including superusers)
            if request.user.is_superuser or request.user.has_permission(permission_name):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "You don't have permission to access this page")
            return redirect('adminlogin')
        return _wrapped_view
    return decorator