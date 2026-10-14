from django.db import models
from django.conf import settings
from django.utils import timezone
import random

class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile'
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, db_index=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default='Jaipur')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Enquiry(models.Model):
    class EventType(models.TextChoices):
        WEDDING = 'wedding', 'Wedding'
        RECEPTION = 'reception', 'Reception'
        ENGAGEMENT = 'engagement', 'Engagement'
        SANGEET = 'sangeet', 'Sangeet'
        MEHNDI = 'mehndi', 'Mehndi'
        HALDI = 'haldi', 'Haldi'
        BIRTHDAY = 'birthday', 'Birthday'
        RELIGIOUS = 'religious', 'Religious Function'
        CORPORATE = 'corporate', 'Corporate Event'
        EXHIBITION = 'exhibition', 'Exhibition'
        OTHER = 'other', 'Other Event'

    class Status(models.TextChoices):
        NEW = 'new', 'New Enquiry'
        CONTACTED = 'contacted', 'Contacted'
        QUOTATION_SENT = 'quotation_sent', 'Quotation Sent'
        NEGOTIATION = 'negotiation', 'In Negotiation'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    enquiry_number = models.CharField(max_length=35, unique=True, db_index=True, blank=True)
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, db_index=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        default=EventType.WEDDING
    )
    event_date = models.DateField(db_index=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.TextField(help_text='Venue or locality/address')
    guest_count = models.PositiveIntegerField(default=200)
    required_services = models.TextField(blank=True, help_text='e.g., Waterproof Tent, Mandap, Stage, 300 Chairs, Generator')
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    additional_requirements = models.TextField(blank=True)
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.NEW
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Enquiries'

    def save(self, *args, **kwargs):
        if not self.enquiry_number:
            year = timezone.now().year
            count = Enquiry.objects.filter(created_at__year=year).count() + 1
            self.enquiry_number = f"VTH-ENQ-{year}-{count:04d}"
        if not self.whatsapp_number and self.phone:
            self.whatsapp_number = self.phone
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enquiry_number} - {self.customer_name} ({self.get_event_type_display()} on {self.event_date})"


class Booking(models.Model):
    class Status(models.TextChoices):
        ENQUIRY = 'enquiry', 'Enquiry Phase'
        QUOTATION = 'quotation', 'Quotation Stage'
        PENDING_CONFIRMATION = 'pending_confirmation', 'Pending Confirmation'
        CONFIRMED = 'confirmed', 'Confirmed'
        IN_PREPARATION = 'in_preparation', 'In Preparation'
        EVENT_ONGOING = 'event_ongoing', 'Event Ongoing'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    booking_id = models.CharField(max_length=35, unique=True, db_index=True, blank=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    enquiry = models.OneToOneField(
        Enquiry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking'
    )
    event_type = models.CharField(max_length=50, default='Wedding')
    event_date = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True, help_text='Optional for multi-day events')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.TextField()
    guest_count = models.PositiveIntegerField(default=250)
    package = models.ForeignKey(
        'services.Package',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    special_instructions = models.TextField(blank=True)

    # Financial summaries
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_CONFIRMATION
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_id:
            year = timezone.now().year
            count = Booking.objects.filter(created_at__year=year).count() + 1
            self.booking_id = f"VTH-BKG-{year}-{count:04d}"
        if not self.end_date:
            self.end_date = self.event_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.customer.name} ({self.event_type} on {self.event_date})"

    @property
    def final_amount(self):
        return max(0, self.total_amount - self.discount)

    @property
    def total_paid(self):
        payments_sum = self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return payments_sum

    @property
    def remaining_balance(self):
        return max(0, self.final_amount - self.total_paid)

    @property
    def payment_status(self):
        paid = self.total_paid
        final = self.final_amount
        if final == 0:
            return 'N/A'
        if paid <= 0:
            return 'Unpaid'
        elif paid < final:
            return 'Partially Paid'
        else:
            return 'Fully Paid'


class BookingItem(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking_allocations'
    )
    item_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} x {self.quantity} for {self.booking.booking_id}"


class EventChecklist(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='checklist_items'
    )
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"[{status}] {self.title} ({self.booking.booking_id})"


class StaffAssignment(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='staff_assignments'
    )
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_assignments'
    )
    role_in_event = models.CharField(
        max_length=100,
        help_text='e.g., Lead Supervisor, Setup Worker, Electrician, Decorator, Driver'
    )
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('booking', 'staff_member', 'role_in_event')
        ordering = ['booking', 'role_in_event']

    def __str__(self):
        return f"{self.staff_member.get_full_name() or self.staff_member.username} as {self.role_in_event} on {self.booking.booking_id}"
