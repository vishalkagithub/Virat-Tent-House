import os
from django.db import models
from django.conf import settings

class BrandConfig(models.Model):
    """
    Dynamic brand configuration for Virat Tent House.
    Allows changing contact details, branding, and addresses without modifying code.
    """
    business_name = models.CharField(max_length=150, default="Virat Tent House")
    tagline = models.CharField(
        max_length=255,
        default="Premium Wedding Decor, Shamiana & Event Infrastructure"
    )
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    phone_number = models.CharField(max_length=25, default="+91 9453402167")
    whatsapp_number = models.CharField(max_length=25, default="919453402167")
    email = models.EmailField(default="virattenthouse@gmail.com")
    address = models.TextField(
        default="Kurki Bazar, Akbarpur-Baskhari road, Ambedkar Nagar, UP, 224210"
    )
    google_maps_url = models.URLField(
        default="https://maps.app.goo.gl/YhDC7fe9LJr8NqSCA"
    )
    google_maps_embed = models.TextField(
        blank=True,
        default="https://maps.google.com/maps?q=Kurki+Bazar,+Akbarpur-Baskhari+road,+Ambedkar+Nagar,+Uttar+Pradesh+224210&t=&z=14&ie=UTF8&iwloc=&output=embed",
        help_text="Embed iframe URL for Google Maps"
    )
    working_hours = models.CharField(max_length=100, default="Monday - Sunday: 8:00 AM - 10:00 PM")
    facebook_url = models.URLField(blank=True, default="https://facebook.com")
    instagram_url = models.URLField(blank=True, default="https://instagram.com")
    youtube_url = models.URLField(blank=True, default="https://youtube.com")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Brand Configuration"
        verbose_name_plural = "Brand Configuration"

    def __str__(self):
        return self.business_name

    @classmethod
    def get_config(cls):
        config, created = cls.objects.get_or_create(id=1)
        return config


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ENQUIRY = 'enquiry', 'New Customer Enquiry'
        QUOTATION = 'quotation', 'Quotation Update'
        BOOKING = 'booking', 'Booking Update'
        PAYMENT = 'payment', 'Payment Received'
        INVENTORY_ALERT = 'inventory_alert', 'Inventory Alert'
        EVENT_REMINDER = 'event_reminder', 'Event Preparation Reminder'
        SYSTEM = 'system', 'System Notification'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="Recipient user or empty for all staff/admins"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"
