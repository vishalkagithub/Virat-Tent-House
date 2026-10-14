from django import forms
from .models import Service, Package, ServiceCategory, PackageItem

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'name', 'description', 'pricing_type', 'base_price', 'unit_name', 'featured', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pricing_type': forms.Select(attrs={'class': 'form-select'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_name': forms.TextInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'description', 'starting_price', 'image', 'terms', 'featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
