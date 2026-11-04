from django import forms
from django.contrib.auth import get_user_model
from .models import ServiceRequest, RequestCategory, RequestPriority, RequestDepartment

User = get_user_model()


class ServiceRequestForm(forms.ModelForm):
    """Used by guests to submit a service request."""
    class Meta:
        model  = ServiceRequest
        fields = ['category', 'title', 'description', 'priority']
        widgets = {
            'category':    forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'title':       forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Brief description of your request'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Additional details (optional)'}),
            'priority':    forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Guests cannot mark things URGENT (that's for staff)
        self.fields['priority'].choices = [
            (RequestPriority.LOW,    'Low — Not urgent'),
            (RequestPriority.NORMAL, 'Normal'),
            (RequestPriority.HIGH,   'High — Needs attention soon'),
        ]
        # Remove EMERGENCY from category in normal form (use emergency button instead)
        self.fields['category'].choices = [
            c for c in RequestCategory.choices if c[0] != 'EMERGENCY'
        ]


class AssignRequestForm(forms.ModelForm):
    """Used by receptionists/managers to assign a request to a staff member."""
    class Meta:
        model  = ServiceRequest
        fields = ['assigned_to', 'department', 'priority', 'internal_notes']
        widgets = {
            'assigned_to':    forms.Select(attrs={'class': 'form-select'}),
            'department':     forms.Select(attrs={'class': 'form-select'}),
            'priority':       forms.Select(attrs={'class': 'form-select'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes for the assigned staff member'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active staff accounts (not guests)
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_active=True,
            is_guest_user=False
        ).order_by('first_name')
        self.fields['assigned_to'].empty_label = '— Select staff member —'
        self.fields['assigned_to'].required    = True


class StaffResponseForm(forms.ModelForm):
    """Staff response/completion notes."""
    class Meta:
        model  = ServiceRequest
        fields = ['staff_response', 'internal_notes']
        widgets = {
            'staff_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Message visible to guest'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Internal notes (not shown to guest)'}),
        }


class MessageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':  2,
            'placeholder': 'Type your message...',
        }),
        max_length=1000
    )
