from django.db import models
from django.conf import settings
from django.utils.text import slugify

class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Inventory Category'
        verbose_name_plural = 'Inventory Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    total_quantity = models.PositiveIntegerField(
        default=0,
        help_text='Total physical stock owned'
    )
    available_quantity = models.PositiveIntegerField(
        default=0,
        help_text='Base unallocated / ready stock in warehouse'
    )
    damaged_quantity = models.PositiveIntegerField(
        default=0,
        help_text='Items currently damaged'
    )
    under_maintenance = models.PositiveIntegerField(
        default=0,
        help_text='Items currently undergoing repair'
    )
    unit = models.CharField(max_length=30, default='Pieces')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Standard rental rate per event/day in INR (₹)'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='inventory/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.sku}) - Stock: {self.total_quantity} {self.unit}"

    @property
    def ready_stock(self):
        """Current physical stock available in godown excluding damaged/maintenance."""
        return max(0, self.total_quantity - (self.damaged_quantity + self.under_maintenance))

    def check_availability(self, start_date, end_date=None, requested_quantity=0, exclude_booking_id=None):
        """
        Calculates dynamic availability for a specific event date range by checking
        all overlapping confirmed and active bookings.
        """
        if not end_date:
            end_date = start_date

        from bookings.models import BookingItem

        # Overlapping bookings: event_date <= requested_end_date and (end_date >= requested_start_date or event_date >= requested_start_date)
        overlapping_items = BookingItem.objects.filter(
            inventory_item=self,
            booking__status__in=['confirmed', 'in_preparation', 'event_ongoing'],
            booking__event_date__lte=end_date,
        )

        # Handle multi-day vs single-day booking logic
        overlapping_items = overlapping_items.filter(
            models.Q(booking__end_date__gte=start_date) |
            models.Q(booking__end_date__isnull=True, booking__event_date__gte=start_date)
        )

        if exclude_booking_id:
            overlapping_items = overlapping_items.exclude(booking_id=exclude_booking_id)

        booked_quantity = overlapping_items.aggregate(
            total_booked=models.Sum('quantity')
        )['total_booked'] or 0

        usable_stock = self.ready_stock
        available_for_date = max(0, usable_stock - booked_quantity)
        shortage = max(0, requested_quantity - available_for_date)

        return {
            'total_stock': self.total_quantity,
            'damaged_or_maintenance': self.damaged_quantity + self.under_maintenance,
            'usable_stock': usable_stock,
            'booked_quantity': booked_quantity,
            'available_for_date': available_for_date,
            'requested_quantity': requested_quantity,
            'shortage': shortage,
            'is_available': shortage == 0
        }


class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        PURCHASE = 'purchase', 'New Purchase'
        DISPATCH = 'dispatch', 'Event Dispatch'
        RETURN = 'return', 'Event Return'
        DAMAGE = 'damage', 'Reported Damaged'
        REPAIR = 'repair', 'Restored from Repair'
        AUDIT = 'audit', 'Stock Audit Adjustment'

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    quantity = models.IntegerField(help_text='Positive for addition, negative for deduction')
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_transactions'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item.name} - {self.get_transaction_type_display()} ({self.quantity}) on {self.created_at.strftime('%d-%b-%Y')}"


class EventInventoryDispatch(models.Model):
    class DispatchStatus(models.TextChoices):
        PREPARED = 'prepared', 'Prepared in Godown'
        LOADED = 'loaded', 'Loaded on Vehicle'
        DISPATCHED = 'dispatched', 'Dispatched to Venue'
        DELIVERED = 'delivered', 'Delivered at Venue'
        INSTALLED = 'installed', 'Installed & Ready'
        RETURNED = 'returned', 'Returned to Godown'

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='dispatches'
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='event_dispatches'
    )
    issued_quantity = models.PositiveIntegerField(default=0)
    returned_quantity = models.PositiveIntegerField(default=0)
    damaged_quantity = models.PositiveIntegerField(default=0)
    missing_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=DispatchStatus.choices,
        default=DispatchStatus.PREPARED
    )
    dispatched_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['booking', 'item']
        unique_together = ('booking', 'item')

    def __str__(self):
        return f"Booking #{self.booking.booking_id} - {self.item.name} ({self.issued_quantity} {self.item.unit})"

    def process_return(self, returned_qty, damaged_qty, missing_qty, staff_user=None):
        """
        Processes return from event:
        - Updates returned, damaged, and missing counts
        - Creates transactions and adjusts damaged stock
        """
        self.returned_quantity = returned_qty
        self.damaged_quantity = damaged_qty
        self.missing_quantity = missing_qty
        self.status = self.DispatchStatus.RETURNED
        self.save()

        # Update inventory item damaged count
        if damaged_qty > 0:
            self.item.damaged_quantity += damaged_qty
            self.item.save(update_fields=['damaged_quantity'])
            InventoryTransaction.objects.create(
                item=self.item,
                transaction_type=InventoryTransaction.TransactionType.DAMAGE,
                quantity=-damaged_qty,
                booking=self.booking,
                notes=f"Damaged during event {self.booking.booking_id}",
                created_by=staff_user
            )

        if missing_qty > 0:
            self.item.total_quantity = max(0, self.item.total_quantity - missing_qty)
            self.item.save(update_fields=['total_quantity'])
            InventoryTransaction.objects.create(
                item=self.item,
                transaction_type=InventoryTransaction.TransactionType.AUDIT,
                quantity=-missing_qty,
                booking=self.booking,
                notes=f"Missing after event {self.booking.booking_id}",
                created_by=staff_user
            )
