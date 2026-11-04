from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model  = InventoryItem
        fields = ['name', 'department', 'quantity', 'unit', 'minimum_level', 'description']
        widgets = {
            'name':          forms.TextInput(attrs={'class': 'form-control'}),
            'department':    forms.Select(attrs={'class': 'form-select'}),
            'quantity':      forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unit':          forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'description':   forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
