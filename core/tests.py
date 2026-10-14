from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import BrandConfig

User = get_user_model()

class CoreViewsAndSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.brand = BrandConfig.get_config()
        self.staff_user = User.objects.create_user(
            username='staff_test', password='password123', role=User.Role.STAFF
        )
        self.customer_user = User.objects.create_user(
            username='cust_test', password='password123', role=User.Role.CUSTOMER
        )

    def test_public_pages_load_successfully(self):
        # Home
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.brand.business_name)

        # About
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

        # Contact
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

        # Services List
        response = self.client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)

        # Packages List
        response = self.client.get(reverse('services:package_list'))
        self.assertEqual(response.status_code, 200)

        # Enquiry Form
        response = self.client.get(reverse('bookings:enquiry_create'))
        self.assertEqual(response.status_code, 200)

        # Robots & Sitemap
        self.assertEqual(self.client.get(reverse('core:robots_txt')).status_code, 200)
        self.assertEqual(self.client.get(reverse('core:sitemap_xml')).status_code, 200)

    def test_dashboard_access_control(self):
        # Anonymous user should be redirected to login
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)

        # Customer user should be denied access (403 PermissionDenied)
        self.client.login(username='cust_test', password='password123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Staff user should successfully access dashboard
        self.client.login(username='staff_test', password='password123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Business Operations Dashboard")

    def test_api_endpoints_read_only_public(self):
        response = self.client.get('/api/services/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/packages/')
        self.assertEqual(response.status_code, 200)
