"""
core/views.py

Core views: the home page and the smart dashboard router.

The dashboard router reads the logged-in user's role and sends them
to the right dashboard — reception, maintenance, housekeeping, etc.
This means each staff member always lands on their relevant page.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    """
    The public-facing home page.
    If already logged in: send to dashboard.
    If not: show the hotel landing page with login/guest portal options.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    """
    Smart dashboard router.

    Reads request.user.role and redirects to the right dashboard.
    This single URL (/dashboard/) is safe to bookmark — it always
    takes you to your own section.
    """
    user = request.user

    # Guest accounts go to the guest portal
    if user.is_guest_user:
        return redirect('guests:portal_entry')

    # Route staff to their department dashboard
    role_redirect_map = {
        'SUPER_ADMIN':    'reports:dashboard',
        'MANAGER':        'reports:dashboard',
        'RECEPTIONIST':   'requests_app:reception_dashboard',
        'HOUSEKEEPING':   'housekeeping:dashboard',
        'MAINTENANCE':    'maintenance:dashboard',
        'RESTAURANT':     'restaurant:dashboard',
        'LAUNDRY':        'requests_app:department_dashboard',
        'SECURITY':       'requests_app:department_dashboard',
        'TRANSPORTATION': 'requests_app:department_dashboard',
    }

    target = role_redirect_map.get(user.role, 'requests_app:reception_dashboard')
    return redirect(target)
