from datetime import date
from django.test import TestCase
from .models import Quotation, QuotationItem
from .pdf_generator import generate_quotation_pdf
from bookings.models import Customer
from core.models import BrandConfig

class FinanceQuotationAndPdfTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Pooja Agarwal', phone='9829044444')
        self.brand = BrandConfig.get_config()

    def test_quotation_calculations(self):
        quotation = Quotation.objects.create(
            customer=self.customer,
            event_type='Sangeet',
            event_date=date(2026, 11, 30),
            venue='Jaipur Heritage Resort',
            discount=5000,
            tax_rate=18
        )

        QuotationItem.objects.create(
            quotation=quotation,
            description='Shamiana Tent Setup',
            quantity=1,
            unit_price=40000
        )
        QuotationItem.objects.create(
            quotation=quotation,
            description='Banquet Chairs with Ribbons',
            quantity=200,
            unit_price=50
        )

        quotation.calculate_totals()
        # subtotal = 40000 + (200*50 = 10000) = 50000
        self.assertEqual(quotation.subtotal, 50000)
        # taxable = 50000 - 5000 discount = 45000
        # tax = 45000 * 0.18 = 8100
        self.assertEqual(quotation.tax_amount, 8100)
        # grand total = 45000 + 8100 = 53100
        self.assertEqual(quotation.grand_total, 53100)
        # advance required 30% of 53100 = 15930
        self.assertEqual(quotation.advance_required, 15930)

    def test_pdf_generation(self):
        quotation = Quotation.objects.create(
            customer=self.customer,
            event_type='Wedding',
            event_date=date(2026, 12, 1),
            venue='Rambagh Lawns',
            subtotal=80000,
            grand_total=80000
        )
        QuotationItem.objects.create(
            quotation=quotation,
            description='Royal Mandap & Floral Decor',
            quantity=1,
            unit_price=80000
        )

        pdf_buffer = generate_quotation_pdf(quotation, self.brand)
        pdf_bytes = pdf_buffer.getvalue()
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
