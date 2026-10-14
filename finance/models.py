from django.db import models
from django.conf import settings
from django.utils import timezone

class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent to Client'
        ACCEPTED = 'accepted', 'Accepted / Approved'
        REJECTED = 'rejected', 'Rejected'
        EXPIRED = 'expired', 'Expired'

    quotation_number = models.CharField(max_length=35, unique=True, db_index=True, blank=True)
    customer = models.ForeignKey(
        'bookings.Customer',
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations'
    )
    enquiry = models.ForeignKey(
        'bookings.Enquiry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations'
    )
    title = models.CharField(max_length=200, default="Event Tent & Decoration Quotation")
    event_type = models.CharField(max_length=50, default="Wedding")
    event_date = models.DateField()
    venue = models.TextField()

    # Financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='GST % if applicable (e.g. 18.00 or 0.00)'
    )
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    advance_required = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    valid_until = models.DateField(null=True, blank=True)
    terms_and_conditions = models.TextField(
        blank=True,
        default=(
            "1. 30% advance payment required to confirm booking.\n"
            "2. Remaining balance must be cleared on or before the event date.\n"
            "3. Any damages or missing items during the event will be billed at actual replacement cost.\n"
            "4. Electricity connection and permissions at venue to be arranged by the client.\n"
            "5. Virat Tent House reserves the right to substitute equipment with equal or superior alternatives if necessary."
        )
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            year = timezone.now().year
            count = Quotation.objects.filter(created_at__year=year).count() + 1
            self.quotation_number = f"VTH-QTN-{year}-{count:04d}"
        if not self.valid_until:
            self.valid_until = timezone.now().date() + timezone.timedelta(days=15)
        super().save(*args, **kwargs)

    def calculate_totals(self):
        from decimal import Decimal
        items_sum = self.items.aggregate(
            total=models.Sum('total_price')
        )['total'] or Decimal('0.00')
        self.subtotal = items_sum
        taxable_amt = max(Decimal('0.00'), self.subtotal - self.discount)
        self.tax_amount = round((taxable_amt * self.tax_rate) / Decimal('100'), 2)
        self.grand_total = taxable_amt + self.tax_amount
        if self.advance_required == 0:
            self.advance_required = round(self.grand_total * Decimal('0.30'), 2)
        self.save()

    def __str__(self):
        return f"{self.quotation_number} - {self.customer.name} (₹{self.grand_total:,.2f})"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.quantity} @ ₹{self.unit_price}) for {self.quotation.quotation_number}"


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        UPI = 'upi', 'UPI (GooglePay / PhonePe / Paytm)'
        BANK_TRANSFER = 'bank_transfer', 'Bank NEFT / RTGS / IMPS'
        CARD = 'card', 'Debit / Credit Card'
        OTHER = 'other', 'Other'

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now, db_index=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.UPI
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='UPI reference, Bank UTR, or receipt number'
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Payment ₹{self.amount:,.2f} on {self.booking.booking_id} via {self.get_payment_method_display()}"


class Expense(models.Model):
    class Category(models.TextChoices):
        TRANSPORT = 'transport', 'Transport & Fuel'
        LABOUR = 'labour', 'Labour & Daily Wage'
        MATERIALS = 'materials', 'Decoration Materials & Fabrics'
        REPAIR = 'repair', 'Repair & Welding'
        ELECTRICITY = 'electricity', 'Electricity & Genset Fuel'
        STAFF = 'staff', 'Staff Salaries / Allowances'
        MAINTENANCE = 'maintenance', 'Warehouse / Godown Maintenance'
        PURCHASES = 'purchases', 'New Equipment Purchase'
        MISCELLANEOUS = 'miscellaneous', 'Miscellaneous'

    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField(default=timezone.now, db_index=True)
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.MISCELLANEOUS
    )
    description = models.TextField(blank=True)
    related_booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        help_text='Associate with a specific event if applicable'
    )
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} - ₹{self.amount:,.2f} ({self.get_category_display()})"
