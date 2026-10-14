from django import forms
from .models import Quotation, QuotationItem, Payment, Expense
from bookings.models import Booking, Customer

class QuotationForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    booking = forms.ModelChoiceField(
        queryset=Booking.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Quotation
        fields = [
            'customer', 'booking', 'title', 'event_type', 'event_date', 'venue',
            'discount', 'tax_rate', 'advance_required', 'valid_until', 'terms_and_conditions', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.TextInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'venue': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 18.00'}),
            'advance_required': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['service', 'description', 'quantity', 'unit_price']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description / service detail'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'payment_date', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. UPI / UTR / Cash Voucher #'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'expense_date', 'category', 'related_booking', 'description', 'receipt']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'related_booking': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
