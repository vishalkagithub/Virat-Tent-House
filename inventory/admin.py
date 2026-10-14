from django.contrib import admin
from .models import InventoryCategory, InventoryItem, InventoryTransaction, EventInventoryDispatch

@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sku', 'total_quantity', 'available_quantity', 'damaged_quantity', 'under_maintenance', 'unit', 'rental_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'transaction_type', 'quantity', 'booking', 'created_by', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('item__name', 'notes')
    date_hierarchy = 'created_at'

@admin.register(EventInventoryDispatch)
class EventInventoryDispatchAdmin(admin.ModelAdmin):
    list_display = ('booking', 'item', 'issued_quantity', 'returned_quantity', 'damaged_quantity', 'missing_quantity', 'status')
    list_filter = ('status', 'dispatched_at')
    search_fields = ('booking__booking_id', 'item__name')
