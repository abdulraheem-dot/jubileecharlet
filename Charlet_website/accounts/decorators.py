"""
accounts/decorators.py

Custom permission decorators.

A DECORATOR is a function that wraps another function to add behaviour.
In Django, view decorators add permission checks before the view runs.

Example usage in views.py:
    @login_required
    @manager_required
    def my_view(request):
        ...

If the user is not a manager, they see a 403 Forbidden page
(or get redirected with an error message) instead of the view.

HOW DECORATORS WORK:
    @manager_required
    def my_view(request):
        ...

Is equivalent to:
    def my_view(request):
        ...
    my_view = manager_required(my_view)

So manager_required wraps my_view, adds a check, then either
calls the real view or returns an error response.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Generic decorator: requires the user to have one of the listed roles.

    Usage:
        @role_required('MANAGER', 'SUPER_ADMIN')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)  # Preserves the original function's name and docstring
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                "You do not have permission to access that page."
            )
            return redirect('core:dashboard')
        return wrapper
    return decorator


def manager_required(view_func):
    """
    Shortcut decorator: requires Manager or Super Admin role.

    Usage:
        @manager_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.is_manager:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Only managers can access this area.")
        return redirect('core:dashboard')
    return wrapper


def super_admin_required(view_func):
    """Requires Super Admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.is_super_admin:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Only super admins can access this area.")
        return redirect('core:dashboard')
    return wrapper


def receptionist_or_above(view_func):
    """Requires Receptionist, Manager, or Super Admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        allowed_roles = ['RECEPTIONIST', 'MANAGER', 'SUPER_ADMIN']
        if request.user.is_superuser or request.user.role in allowed_roles:
            return view_func(request, *args, **kwargs)

        messages.error(request, "You do not have permission to access this area.")
        return redirect('core:dashboard')
    return wrapper


def staff_required(view_func):
    """Requires any logged-in staff member (not a guest account)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.is_guest_user:
            return redirect('guests:portal_entry')

        return view_func(request, *args, **kwargs)
    return wrapper
