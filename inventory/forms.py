from django import forms
from .models import InventoryItem, InventoryCategory, EventInventoryDispatch

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'category', 'name', 'sku', 'total_quantity', 'available_quantity',
            'damaged_quantity', 'under_maintenance', 'unit', 'purchase_price',
            'rental_price', 'description', 'image', 'is_active'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CHR-MAH-01'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'damaged_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'under_maintenance': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Pieces, Sets, Sq Ft'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rental_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventoryAvailabilityCheckForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text='Leave empty if single-day event'
    )
    requested_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 250'})
    )


class EventDispatchForm(forms.ModelForm):
    class Meta:
        model = EventInventoryDispatch
        fields = ['item', 'issued_quantity', 'status', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'issued_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EventReturnForm(forms.Form):
    returned_quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    damaged_quantity = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    missing_quantity = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
