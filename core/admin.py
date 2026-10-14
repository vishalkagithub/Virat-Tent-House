from django.contrib import admin
from .models import BrandConfig, Notification

@admin.register(BrandConfig)
class BrandConfigAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'phone_number', 'whatsapp_number', 'email', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'user', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'
