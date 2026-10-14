from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsRolePermissionsTest(TestCase):
    def setUp(self):
        self.super_admin = User.objects.create_user(
            username='sadmin', password='pass', role=User.Role.SUPER_ADMIN
        )
        self.owner = User.objects.create_user(
            username='biz_owner', password='pass', role=User.Role.OWNER
        )
        self.manager = User.objects.create_user(
            username='mgr', password='pass', role=User.Role.MANAGER
        )
        self.staff = User.objects.create_user(
            username='stf', password='pass', role=User.Role.STAFF
        )
        self.customer = User.objects.create_user(
            username='cust', password='pass', role=User.Role.CUSTOMER
        )

    def test_role_hierarchy_properties(self):
        # Super admin tests
        self.assertTrue(self.super_admin.is_super_admin)
        self.assertTrue(self.super_admin.is_owner)
        self.assertTrue(self.super_admin.is_manager)
        self.assertTrue(self.super_admin.is_staff_member)
        self.assertFalse(self.super_admin.is_customer)

        # Owner tests
        self.assertTrue(self.owner.is_owner)
        self.assertTrue(self.owner.is_manager)
        self.assertTrue(self.owner.is_staff_member)
        self.assertFalse(self.owner.is_customer)

        # Manager tests
        self.assertFalse(self.manager.is_owner)
        self.assertTrue(self.manager.is_manager)
        self.assertTrue(self.manager.is_staff_member)
        self.assertFalse(self.manager.is_customer)

        # Staff tests
        self.assertFalse(self.staff.is_manager)
        self.assertTrue(self.staff.is_staff_member)
        self.assertFalse(self.staff.is_customer)

        # Customer tests
        self.assertFalse(self.customer.is_staff_member)
        self.assertTrue(self.customer.is_customer)
