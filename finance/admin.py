from django.contrib import admin
from .models import Quotation, QuotationItem, Payment, Expense

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quotation_number', 'customer', 'event_type', 'event_date', 'grand_total', 'status', 'valid_until', 'created_at')
    list_filter = ('status', 'event_date')
    search_fields = ('quotation_number', 'customer__name', 'venue')
    inlines = [QuotationItemInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_date', 'payment_method', 'transaction_id', 'recorded_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('booking__booking_id', 'transaction_id')
    date_hierarchy = 'payment_date'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'expense_date', 'related_booking', 'added_by')
    list_filter = ('category', 'expense_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'expense_date'
