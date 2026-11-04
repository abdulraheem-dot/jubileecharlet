"""
accounts/admin.py

Registers our custom User and StaffProfile models with Django's admin interface.

Django admin gives us a powerful built-in interface to:
- Create and manage users
- Assign roles
- View and edit staff profiles

We customise it here so the admin panel shows the right columns and filters.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StaffProfile


# ---------------------------------------------------------------------------
# STAFF PROFILE INLINE
# ---------------------------------------------------------------------------
# An inline lets us edit the StaffProfile on the same page as the User.
# Instead of navigating to a separate form, the staff profile fields
# appear right inside the user edit page.
class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'
    # Show these fields inside the User admin page
    fields = ['department', 'employee_number', 'shift', 'is_on_duty', 'date_hired', 'bio', 'profile_photo']


# ---------------------------------------------------------------------------
# CUSTOM USER ADMIN
# ---------------------------------------------------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    We extend Django's built-in UserAdmin to include our custom fields.
    BaseUserAdmin already handles password hashing and permissions tabs.
    We just add our extra fields on top.
    """
    inlines = [StaffProfileInline]

    # Columns shown in the user list view
    list_display = ['username', 'get_full_name', 'email', 'role', 'is_guest_user', 'is_active', 'date_joined']
    list_filter  = ['role', 'is_guest_user', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['first_name']

    # Add our custom fields to the edit form
    # fieldsets controls how fields are grouped on the edit page
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Hotel Information', {
            'fields': ('role', 'is_guest_user', 'phone_number')
        }),
    )

    # Fields shown when CREATING a new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Hotel Information', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'phone_number')
        }),
    )


# ---------------------------------------------------------------------------
# STAFF PROFILE ADMIN (standalone view)
# ---------------------------------------------------------------------------
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'department', 'employee_number', 'shift', 'is_on_duty']
    list_filter   = ['department', 'shift', 'is_on_duty']
    search_fields = ['user__first_name', 'user__last_name', 'employee_number']
    list_editable = ['is_on_duty']
