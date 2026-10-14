from django.contrib import admin
from .models import ServiceCategory, Service, Package, PackageItem

class PackageItemInline(admin.TabularInline):
    model = PackageItem
    extra = 1

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'pricing_type', 'base_price', 'unit_name', 'featured', 'is_active')
    list_filter = ('category', 'pricing_type', 'featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'starting_price', 'featured', 'is_active')
    list_filter = ('featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PackageItemInline]
