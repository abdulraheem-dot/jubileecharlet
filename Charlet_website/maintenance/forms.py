from django import forms
from .models import MaintenanceRecord


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model  = MaintenanceRecord
        fields = ['room', 'category', 'title', 'description', 'priority', 'assigned_to', 'photo']
        widgets = {
            'room':        forms.Select(attrs={'class': 'form-select'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority':    forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['assigned_to'].queryset = User.objects.filter(
            role='MAINTENANCE', is_active=True
        )
        self.fields['assigned_to'].required = False
