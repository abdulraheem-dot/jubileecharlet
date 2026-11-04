"""
accounts/forms.py

Django forms handle user input — they:
1. Render HTML input fields in templates
2. Validate the submitted data
3. Clean and return safe Python values

We create forms for:
- Staff login
- Creating new staff accounts
- Editing staff profiles
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import StaffProfile, Role, Department

# get_user_model() returns our custom User class (accounts.User)
# Always use this instead of importing User directly, to respect AUTH_USER_MODEL
User = get_user_model()


# ---------------------------------------------------------------------------
# LOGIN FORM
# ---------------------------------------------------------------------------
class StaffLoginForm(AuthenticationForm):
    """
    Inherits Django's built-in AuthenticationForm.
    AuthenticationForm already handles:
    - username + password fields
    - checking credentials against the database
    - rate limiting / brute force protection

    We just add Bootstrap CSS classes to the fields.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
        })
    )


# ---------------------------------------------------------------------------
# CREATE STAFF FORM
# ---------------------------------------------------------------------------
class StaffCreationForm(UserCreationForm):
    """
    Form for creating a new staff account.
    Inherits UserCreationForm which adds:
    - password1, password2 (with confirmation matching validation)
    - password strength validation

    We add our custom hotel fields on top.
    """

    # Extra fields from StaffProfile
    department    = forms.ChoiceField(choices=Department.choices, required=False)
    employee_number = forms.CharField(max_length=20, required=False)
    shift         = forms.ChoiceField(choices=StaffProfile.Shift.choices, required=False)
    date_hired    = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'phone_number', 'role', 'password1', 'password2',
        ]
        widgets = {
            'first_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'username':      forms.TextInput(attrs={'class': 'form-control'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number':  forms.TextInput(attrs={'class': 'form-control'}),
            'role':          forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to the password fields that come from UserCreationForm
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['department'].widget.attrs.update({'class': 'form-select'})
        self.fields['shift'].widget.attrs.update({'class': 'form-select'})
        self.fields['date_hired'].widget.attrs.update({'class': 'form-control'})
        self.fields['employee_number'].widget.attrs.update({'class': 'form-control'})
        # first_name and last_name are optional in default Django — make them required
        self.fields['first_name'].required = True
        self.fields['last_name'].required  = True
        self.fields['email'].required      = True

    def save(self, commit=True):
        """
        Override save() to also create the StaffProfile.
        super().save() creates the User record.
        Then we create the linked StaffProfile.
        """
        user = super().save(commit=False)
        user.is_guest_user = False

        if commit:
            user.save()
            # Create the staff profile linked to this user
            StaffProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                employee_number=self.cleaned_data.get('employee_number') or None,
                shift=self.cleaned_data.get('shift') or None,
                date_hired=self.cleaned_data.get('date_hired'),
            )
        return user


# ---------------------------------------------------------------------------
# EDIT STAFF USER FORM
# ---------------------------------------------------------------------------
class StaffEditForm(forms.ModelForm):
    """Form for editing an existing staff member's basic user information."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role']
        widgets = {
            'first_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role':         forms.Select(attrs={'class': 'form-select'}),
        }


# ---------------------------------------------------------------------------
# EDIT STAFF PROFILE FORM
# ---------------------------------------------------------------------------
class StaffProfileEditForm(forms.ModelForm):
    """Form for editing a staff member's hotel profile information."""

    class Meta:
        model = StaffProfile
        fields = ['department', 'employee_number', 'shift', 'is_on_duty', 'date_hired', 'bio', 'profile_photo']
        widgets = {
            'department':      forms.Select(attrs={'class': 'form-select'}),
            'employee_number': forms.TextInput(attrs={'class': 'form-control'}),
            'shift':           forms.Select(attrs={'class': 'form-select'}),
            'is_on_duty':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_hired':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio':             forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
