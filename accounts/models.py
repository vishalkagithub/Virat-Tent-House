from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', _('Super Admin')
        OWNER = 'owner', _('Business Owner')
        MANAGER = 'manager', _('Manager')
        STAFF = 'staff', _('Staff')
        CUSTOMER = 'customer', _('Customer')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text=_('User permission role in the system')
    )
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    address = models.TextField(blank=True)

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.username})" if full_name else self.username

    @property
    def is_super_admin(self):
        return self.is_superuser or self.role == self.Role.SUPER_ADMIN

    @property
    def is_owner(self):
        return self.is_super_admin or self.role == self.Role.OWNER

    @property
    def is_manager(self):
        return self.is_owner or self.role == self.Role.MANAGER

    @property
    def is_staff_member(self):
        return self.is_manager or self.role == self.Role.STAFF

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER


class StaffProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    designation = models.CharField(max_length=100, default='Field Operator')
    skills = models.CharField(
        max_length=255,
        blank=True,
        help_text='e.g., Tent Setup, Mandap Decoration, Lighting, Sound Operator, Driver'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    joining_date = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.designation}"
