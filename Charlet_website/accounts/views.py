"""
accounts/views.py

Views handle HTTP requests and return HTTP responses.

DJANGO VIEW PATTERN:
1. Browser sends a request (e.g. GET /accounts/login/)
2. Django matches the URL to a view function or class
3. The view processes the request (reads data, checks forms, queries DB)
4. The view returns a rendered HTML page (or a redirect)

We use:
- Function-based views (FBV) — simple functions that take `request` and return a response
- Class-based views (CBV) — classes that inherit Django's generic views for less repetition

DECORATORS used:
- @login_required — redirects to login page if user is not authenticated
- @require_POST  — only allows POST requests (prevents direct URL access of form submissions)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.sessions.models import Session

from .forms import StaffLoginForm, StaffCreationForm, StaffEditForm, StaffProfileEditForm
from .models import StaffProfile, Role
from .decorators import manager_required, super_admin_required

User = get_user_model()


# ---------------------------------------------------------------------------
# LOGIN VIEW
# ---------------------------------------------------------------------------
def login_view(request):
    """
    Handles the staff login page.

    GET request:  show the empty login form
    POST request: validate credentials and log the user in

    request.method tells us if the browser is:
    - 'GET'  → just loading the page
    - 'POST' → submitting a form
    """
    # If the user is already logged in, send them to the dashboard
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        # Create the form with the submitted data (request.POST)
        form = StaffLoginForm(request, data=request.POST)

        if form.is_valid():
            # form.get_user() returns the authenticated User object
            user = form.get_user()

            # Don't allow guest accounts to log in through the staff portal
            if user.is_guest_user:
                messages.error(request, "Please use the guest portal to access your account.")
                return redirect('guests:portal_entry')

            # login() creates a session for this user
            # From this point, request.user will return this user in all views
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")

            # If the user was trying to access a specific page before login,
            # send them there after logging in (stored in ?next= query param)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = StaffLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


# ---------------------------------------------------------------------------
# LOGOUT VIEW
# ---------------------------------------------------------------------------
@login_required
def logout_view(request):
    """
    Logs the user out and redirects to the login page.
    logout() deletes the session cookie, so the user is no longer authenticated.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


# ---------------------------------------------------------------------------
# STAFF LIST
# ---------------------------------------------------------------------------
@login_required
@manager_required
def staff_list(request):
    """
    Shows a list of all staff members.
    Only managers and super admins can view this.

    QuerySets explained:
    User.objects.all()                  → returns ALL users
    .filter(is_guest_user=False)        → only staff (not guests)
    .select_related('staffprofile')     → fetch linked StaffProfile in ONE SQL query
                                          (avoids N+1 query problem)
    .order_by('first_name')             → sort alphabetically
    """
    staff = User.objects.filter(
        is_guest_user=False
    ).select_related('staffprofile').order_by('first_name', 'last_name')

    # Filter by role if query param provided: /accounts/staff/?role=MAINTENANCE
    role_filter = request.GET.get('role', '')
    if role_filter:
        staff = staff.filter(role=role_filter)

    # Filter by department if query param provided
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        staff = staff.filter(staffprofile__department=dept_filter)

    context = {
        'staff':       staff,
        'roles':       Role.choices,
        'role_filter': role_filter,
        'dept_filter': dept_filter,
        'total_staff': staff.count(),
    }
    return render(request, 'accounts/staff_list.html', context)


# ---------------------------------------------------------------------------
# CREATE STAFF
# ---------------------------------------------------------------------------
@login_required
@manager_required
def staff_create(request):
    """
    Creates a new staff account.

    The form handles:
    1. Validating all fields
    2. Creating the User record with a hashed password
    3. Creating the linked StaffProfile
    """
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            staff_member = form.save()
            messages.success(
                request,
                f"Staff account created for {staff_member.get_full_name()}."
            )
            return redirect('accounts:staff_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'title': 'Add New Staff Member',
        'action': 'Create',
    })


# ---------------------------------------------------------------------------
# EDIT STAFF
# ---------------------------------------------------------------------------
@login_required
@manager_required
def staff_edit(request, pk):
    """
    Edits an existing staff member.

    get_object_or_404(User, pk=pk) does two things:
    1. Queries: SELECT * FROM accounts_user WHERE id = pk
    2. If no user found, automatically returns a 404 error page
       (better than crashing with an exception)
    """
    staff_user = get_object_or_404(User, pk=pk, is_guest_user=False)

    # get_or_create returns a tuple: (object, created_boolean)
    # If the StaffProfile doesn't exist for this user, create it
    profile, _ = StaffProfile.objects.get_or_create(user=staff_user)

    if request.method == 'POST':
        user_form    = StaffEditForm(request.POST, instance=staff_user)
        profile_form = StaffProfileEditForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f"Profile updated for {staff_user.get_full_name()}.")
            return redirect('accounts:staff_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form    = StaffEditForm(instance=staff_user)
        profile_form = StaffProfileEditForm(instance=profile)

    return render(request, 'accounts/staff_edit.html', {
        'staff_user':    staff_user,
        'user_form':     user_form,
        'profile_form':  profile_form,
    })


# ---------------------------------------------------------------------------
# STAFF DETAIL
# ---------------------------------------------------------------------------
@login_required
def staff_detail(request, pk):
    """Shows a single staff member's profile."""
    staff_user = get_object_or_404(User, pk=pk, is_guest_user=False)
    profile, _ = StaffProfile.objects.get_or_create(user=staff_user)

    return render(request, 'accounts/staff_detail.html', {
        'staff_user': staff_user,
        'profile':    profile,
    })


# ---------------------------------------------------------------------------
# MY PROFILE (current user's own profile)
# ---------------------------------------------------------------------------
@login_required
def my_profile(request):
    """Lets a staff member view and edit their own profile."""
    user = request.user
    profile, _ = StaffProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form    = StaffEditForm(request.POST, instance=user)
        profile_form = StaffProfileEditForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:my_profile')
    else:
        user_form    = StaffEditForm(instance=user)
        profile_form = StaffProfileEditForm(instance=profile)

    return render(request, 'accounts/my_profile.html', {
        'user_form':    user_form,
        'profile_form': profile_form,
        'profile':      profile,
    })


# ---------------------------------------------------------------------------
# TOGGLE DUTY STATUS
# ---------------------------------------------------------------------------
@login_required
@require_POST
def toggle_duty(request):
    """
    Quickly toggles a staff member's on-duty status.
    @require_POST ensures this can only be called via form submission, not via
    a direct URL visit — prevents accidental or malicious toggling via links.
    """
    profile, _ = StaffProfile.objects.get_or_create(user=request.user)
    profile.is_on_duty = not profile.is_on_duty
    profile.save()

    status = "on duty" if profile.is_on_duty else "off duty"
    messages.success(request, f"You are now marked as {status}.")
    return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))


# ---------------------------------------------------------------------------
# DEACTIVATE STAFF
# ---------------------------------------------------------------------------
@login_required
@super_admin_required
def staff_deactivate(request, pk):
    """
    Deactivates a staff account (sets is_active=False).
    We never delete accounts — we deactivate them to preserve history.
    Only super admins can deactivate staff.
    """
    staff_user = get_object_or_404(User, pk=pk, is_guest_user=False)

    if staff_user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:staff_list')

    staff_user.is_active = False
    staff_user.save()
    messages.warning(request, f"{staff_user.get_full_name()} has been deactivated.")
    return redirect('accounts:staff_list')


# ---------------------------------------------------------------------------
# REMOVE USER (Admin removes any user — deactivates + logs them out)
# ---------------------------------------------------------------------------
@login_required
@manager_required
@require_POST
def remove_user(request, pk):
    """
    Removes a user by deactivating their account and flushing all their
    active sessions. This effectively logs them out on their end immediately.

    Works for both staff and guest users.
    Only managers and super admins can remove users.
    """
    target_user = get_object_or_404(User, pk=pk)

    # Safety: can't remove yourself
    if target_user == request.user:
        messages.error(request, "You cannot remove your own account.")
        return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))

    # Safety: super admins can only be removed by other super admins
    if target_user.is_superuser and not request.user.is_superuser:
        messages.error(request, "You do not have permission to remove that account.")
        return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))

    user_label = target_user.get_full_name() or target_user.username
    is_guest = target_user.is_guest_user

    # 1. Deactivate the account — prevents future logins
    target_user.is_active = False
    target_user.save()

    # 2. Flush all Django auth sessions belonging to this user.
    #    Session stores _auth_user_id in the decoded data. We iterate
    #    through sessions and delete any that belong to this user.
    sessions_deleted = 0
    for session in Session.objects.iterator():
        try:
            data = session.get_decoded()
            if str(data.get('_auth_user_id', '')) == str(target_user.pk):
                session.delete()
                sessions_deleted += 1
        except Exception:
            # Skip corrupt sessions
            continue

    if is_guest:
        messages.warning(
            request,
            f"Guest user '{user_label}' has been removed. "
            f"They will be logged out immediately."
        )
    else:
        messages.warning(
            request,
            f"Staff user '{user_label}' has been deactivated and logged out "
            f"({sessions_deleted} session(s) terminated)."
        )

    # Redirect back to where the admin came from
    return redirect(request.META.get('HTTP_REFERER', 'accounts:staff_list'))
