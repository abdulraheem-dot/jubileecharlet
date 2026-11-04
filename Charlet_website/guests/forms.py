from django import forms
from .models import Guest, GuestStay
from rooms.models import Room, RoomStatus


class GuestForm(forms.ModelForm):
    class Meta:
        model  = Guest
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'nationality',
                  'id_type', 'id_number', 'special_requirements', 'is_vip']
        widgets = {
            'first_name':           forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':            forms.TextInput(attrs={'class': 'form-control'}),
            'email':                forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number':         forms.TextInput(attrs={'class': 'form-control'}),
            'nationality':          forms.TextInput(attrs={'class': 'form-control'}),
            'id_type':              forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Passport'}),
            'id_number':            forms.TextInput(attrs={'class': 'form-control'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_vip':               forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GuestStayForm(forms.ModelForm):
    class Meta:
        model  = GuestStay
        fields = ['room', 'check_in_date', 'expected_checkout', 'number_of_guests', 'notes']
        widgets = {
            'room':               forms.Select(attrs={'class': 'form-select'}),
            'check_in_date':      forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expected_checkout':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number_of_guests':   forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes':              forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available and reserved rooms
        self.fields['room'].queryset = Room.objects.filter(
            status__in=[RoomStatus.AVAILABLE, RoomStatus.RESERVED]
        ).select_related('room_type')


class GuestPortalLoginForm(forms.Form):
    """Simple form for guest portal access using room number + access token."""
    room_number  = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. 204'})
    )
    access_code  = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Code on your key card'})
    )
