from django import forms
from .models import Room, RoomType


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'floor', 'room_type', 'status', 'housekeeping_status', 'internal_notes']
        widgets = {
            'number':               forms.TextInput(attrs={'class': 'form-control'}),
            'floor':                forms.NumberInput(attrs={'class': 'form-control'}),
            'room_type':            forms.Select(attrs={'class': 'form-select'}),
            'status':               forms.Select(attrs={'class': 'form-select'}),
            'housekeeping_status':  forms.Select(attrs={'class': 'form-select'}),
            'internal_notes':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
