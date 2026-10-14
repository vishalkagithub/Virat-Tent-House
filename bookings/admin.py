from django.contrib import admin
from .models import Customer, Enquiry, Booking, BookingItem, EventChecklist, StaffAssignment

class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 1

class EventChecklistInline(admin.TabularInline):
    model = EventChecklist
    extra = 0

class StaffAssignmentInline(admin.TabularInline):
    model = StaffAssignment
    extra = 0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'whatsapp_number', 'email', 'city', 'created_at')
    search_fields = ('name', 'phone', 'email')

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('enquiry_number', 'customer_name', 'phone', 'event_type', 'event_date', 'guest_count', 'status', 'created_at')
    list_filter = ('status', 'event_type', 'event_date')
    search_fields = ('enquiry_number', 'customer_name', 'phone', 'venue')
    date_hierarchy = 'event_date'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer', 'event_type', 'event_date', 'total_amount', 'discount', 'status', 'created_at')
    list_filter = ('status', 'event_date')
    search_fields = ('booking_id', 'customer__name', 'customer__phone', 'venue')
    date_hierarchy = 'event_date'
    inlines = [BookingItemInline, EventChecklistInline, StaffAssignmentInline]

@admin.register(EventChecklist)
class EventChecklistAdmin(admin.ModelAdmin):
    list_display = ('title', 'booking', 'is_completed', 'assigned_to', 'completed_at')
    list_filter = ('is_completed',)
    search_fields = ('title', 'booking__booking_id')
