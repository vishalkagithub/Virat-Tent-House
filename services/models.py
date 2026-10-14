from django.db import models
from django.utils.text import slugify

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        default='bi-star-fill',
        help_text='Bootstrap icon class name, e.g., bi-gem, bi-lamp, bi-soundwave'
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    class PricingType(models.TextChoices):
        FIXED = 'fixed', 'Fixed Price'
        PER_ITEM = 'per_item', 'Per Item'
        PER_DAY = 'per_day', 'Per Day'
        PER_GUEST = 'per_guest', 'Per Guest'
        PER_SQFT = 'per_sqft', 'Per Square Foot'
        CUSTOM = 'custom', 'Custom Quotation'

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField()
    pricing_type = models.CharField(
        max_length=20,
        choices=PricingType.choices,
        default=PricingType.FIXED
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Base price in INR (₹). If custom, can be 0.00'
    )
    unit_name = models.CharField(
        max_length=50,
        default='Unit',
        help_text='e.g., Day, Piece, Sq Ft, Guest, Setup'
    )
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def price_display(self):
        if self.pricing_type == self.PricingType.CUSTOM:
            return "Custom Quotation"
        return f"₹{self.base_price:,.2f} / {self.unit_name}"


class Package(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField()
    starting_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Starting package price in INR (₹)'
    )
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    terms = models.TextField(
        blank=True,
        default='Standard setup and dismantling included. Transport within city limits included. Power backup charges extra.'
    )
    featured = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['starting_price']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (from ₹{self.starting_price:,.0f})"


class PackageItem(models.Model):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='package_inclusions'
    )
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=200, blank=True, help_text='e.g., 500 Guests capacity, 2 Days setup')

    def __str__(self):
        return f"{self.service.name} x {self.quantity} in {self.package.name}"
