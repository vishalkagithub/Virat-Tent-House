from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StaffProfile

class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Details'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Virat Tent House Role & Contact', {
            'fields': ('role', 'phone', 'address')
        }),
    )
    inlines = [StaffProfileInline]

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'designation', 'skills', 'salary', 'joining_date', 'is_active')
    list_filter = ('designation', 'is_active', 'joining_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'skills')
