"""
accounts/models.py

This file defines the User model and StaffProfile for Jubilee Chalets.

KEY CONCEPTS:
- Django's built-in User model handles username/password/email.
  We EXTEND it by creating our own User class that inherits from AbstractUser.
  This gives us everything Django provides PLUS our own custom fields.

- AbstractUser is Django's full User model in class form.
  By subclassing it, we get login, password hashing, groups, and permissions
  for free — and we can add our own fields.

- Setting AUTH_USER_MODEL = 'accounts.User' in settings.py tells Django
  to use OUR User class instead of the default one.
  This must be done before the first migration.

- StaffProfile is a separate model linked to User with OneToOneField.
  It stores hotel-specific information: department, role, employee number, etc.
  This keeps the User model clean while allowing us to extend staff data.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# ROLE CHOICES
# ---------------------------------------------------------------------------
# These are the staff roles in the hotel.
# Each role controls what the staff member can see and do.
class Role(models.TextChoices):
    """
    TextChoices creates a set of string constants.
    Usage:   Role.RECEPTIONIST  → 'RECEPTIONIST'
    In DB:   stored as the string value e.g. 'RECEPTIONIST'
    In forms/templates: displayed as the human-readable label e.g. 'Receptionist'
    """
    SUPER_ADMIN    = 'SUPER_ADMIN',    'Super Admin'
    MANAGER        = 'MANAGER',        'Manager'
    RECEPTIONIST   = 'RECEPTIONIST',   'Receptionist'
    HOUSEKEEPING   = 'HOUSEKEEPING',   'Housekeeping'
    MAINTENANCE    = 'MAINTENANCE',    'Maintenance'
    RESTAURANT     = 'RESTAURANT',     'Restaurant'
    LAUNDRY        = 'LAUNDRY',        'Laundry'
    SECURITY       = 'SECURITY',       'Security'
    TRANSPORTATION = 'TRANSPORTATION', 'Transportation'


# ---------------------------------------------------------------------------
# DEPARTMENT CHOICES
# ---------------------------------------------------------------------------
class Department(models.TextChoices):
    RECEPTION      = 'RECEPTION',      'Reception'
    HOUSEKEEPING   = 'HOUSEKEEPING',   'Housekeeping'
    MAINTENANCE    = 'MAINTENANCE',    'Maintenance'
    RESTAURANT     = 'RESTAURANT',     'Restaurant'
    LAUNDRY        = 'LAUNDRY',        'Laundry'
    SECURITY       = 'SECURITY',       'Security'
    MANAGEMENT     = 'MANAGEMENT',     'Management'
    TRANSPORTATION = 'TRANSPORTATION', 'Transportation'


# ---------------------------------------------------------------------------
# CUSTOM USER MODEL
# ---------------------------------------------------------------------------
class User(AbstractUser):
    """
    Our custom User model.

    We inherit from AbstractUser which gives us:
    - username, email, password (hashed automatically)
    - first_name, last_name
    - is_staff, is_active, is_superuser
    - date_joined, last_login
    - groups, user_permissions
    - login/logout methods

    We ADD:
    - role: what kind of staff member this user is
    - is_guest_user: flag so we know if this account belongs to a hotel guest
    - phone_number: contact number

    HOW DJANGO STORES PASSWORDS:
    Django NEVER stores plain passwords.
    When you call user.set_password('mypassword'), Django runs it through
    a hashing algorithm (PBKDF2+SHA256 by default) and stores the hash.
    When you log in, Django hashes what you typed and compares the two hashes.
    """

    # The role determines what dashboard and features the user sees
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST,
        help_text="Staff role — controls permissions and dashboard access"
    )

    # Guests get a user account too (for the guest portal)
    # This flag distinguishes guests from staff
    is_guest_user = models.BooleanField(
        default=False,
        help_text="True if this account belongs to a hotel guest, not a staff member"
    )

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # When was this user's profile last updated?
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # __str__ defines how this object appears in Django admin, templates, and print()
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_role_display_badge_class(self):
        """Returns a Bootstrap badge colour class based on role."""
        colour_map = {
            Role.SUPER_ADMIN:    'bg-dark',
            Role.MANAGER:        'bg-primary',
            Role.RECEPTIONIST:   'bg-info text-dark',
            Role.HOUSEKEEPING:   'bg-success',
            Role.MAINTENANCE:    'bg-warning text-dark',
            Role.RESTAURANT:     'bg-danger',
            Role.LAUNDRY:        'bg-secondary',
            Role.SECURITY:       'bg-dark',
            Role.TRANSPORTATION: 'bg-primary',
        }
        return colour_map.get(self.role, 'bg-secondary')

    # -----------------------------------------------------------------------
    # ROLE HELPER PROPERTIES
    # -----------------------------------------------------------------------
    # These @property methods let templates check roles cleanly:
    # e.g.  {% if user.is_receptionist %}  rather than  {% if user.role == 'RECEPTIONIST' %}

    @property
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_manager(self):
        return self.role in [Role.MANAGER, Role.SUPER_ADMIN] or self.is_superuser

    @property
    def is_receptionist(self):
        return self.role == Role.RECEPTIONIST

    @property
    def is_housekeeping_staff(self):
        return self.role == Role.HOUSEKEEPING

    @property
    def is_maintenance_staff(self):
        return self.role == Role.MAINTENANCE

    @property
    def is_restaurant_staff(self):
        return self.role == Role.RESTAURANT

    @property
    def is_security_staff(self):
        return self.role == Role.SECURITY

    @property
    def can_manage_requests(self):
        """Can this user accept, assign, and update requests?"""
        return self.role in [
            Role.SUPER_ADMIN, Role.MANAGER, Role.RECEPTIONIST
        ] or self.is_superuser

    @property
    def can_view_reports(self):
        """Can this user access the reports/analytics section?"""
        return self.role in [Role.SUPER_ADMIN, Role.MANAGER] or self.is_superuser

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['first_name', 'last_name']


# ---------------------------------------------------------------------------
# STAFF PROFILE
# ---------------------------------------------------------------------------
class StaffProfile(models.Model):
    """
    Stores extra hotel-specific information for each staff member.

    WHY A SEPARATE MODEL?
    We don't put everything into the User model because:
    1. It stays clean — User handles login, StaffProfile handles hotel data
    2. Not every user needs a staff profile (guests don't)
    3. Easy to extend later without touching the User model

    OneToOneField means:
    - Each User has at most ONE StaffProfile
    - Each StaffProfile belongs to exactly ONE User
    - Think of it like a JOIN in SQL where both sides are unique

    Accessing from a User instance:
        user.staffprofile.employee_number
        user.staffprofile.department

    Accessing from a StaffProfile instance:
        profile.user.first_name
        profile.user.email
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # If the user is deleted, delete their profile too
        related_name='staffprofile'
    )

    department = models.CharField(
        max_length=20,
        choices=Department.choices,
        blank=True,
        null=True
    )

    employee_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Hotel employee ID number e.g. JC-001"
    )

    profile_photo = models.ImageField(
        upload_to='staff_photos/',
        blank=True,
        null=True
    )

    # Which shift does this staff member work?
    class Shift(models.TextChoices):
        MORNING   = 'MORNING',   'Morning (6am - 2pm)'
        AFTERNOON = 'AFTERNOON', 'Afternoon (2pm - 10pm)'
        NIGHT     = 'NIGHT',     'Night (10pm - 6am)'

    shift = models.CharField(
        max_length=10,
        choices=Shift.choices,
        blank=True,
        null=True
    )

    is_on_duty = models.BooleanField(
        default=False,
        help_text="Is this staff member currently on duty?"
    )

    # Free-text bio or notes
    bio = models.TextField(blank=True, null=True)

    date_hired = models.DateField(blank=True, null=True)

    # When was this profile record created/updated?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.get_department_display()}"

    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
