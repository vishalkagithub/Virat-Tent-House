from django import forms
from .models import Enquiry, Booking, BookingItem, EventChecklist, StaffAssignment, Customer

class CustomerEnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = [
            'customer_name', 'phone', 'whatsapp_number', 'email',
            'event_type', 'event_date', 'start_time', 'end_time',
            'venue', 'guest_count', 'required_services', 'budget',
            'additional_requirements'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9453402167'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Event Venue & Locality in Ambedkar Nagar / UP'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 10}),
            'required_services': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Waterproof German Tent, Royal Mandap, Stage, 400 Banquet Chairs, Genset'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Approximate Budget (₹)'}),
            'additional_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any specific theme colors or timeline preferences'}),
        }


class BookingForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    customer_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    class Meta:
        model = Booking
        fields = [
            'event_type', 'event_date', 'end_date', 'start_time', 'end_time',
            'venue', 'guest_count', 'package', 'total_amount', 'discount',
            'advance_amount', 'status', 'special_instructions'
        ]
        widgets = {
            'event_type': forms.TextInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'package': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'advance_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BookingItemForm(forms.ModelForm):
    class Meta:
        model = BookingItem
        fields = ['service', 'inventory_item', 'item_name', 'quantity', 'unit_price']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
            'inventory_item': forms.Select(attrs={'class': 'form-select'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class StaffAssignmentForm(forms.ModelForm):
    class Meta:
        model = StaffAssignment
        fields = ['staff_member', 'role_in_event', 'notes']
        widgets = {
            'staff_member': forms.Select(attrs={'class': 'form-select'}),
            'role_in_event': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lead Supervisor, Decorator'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }
