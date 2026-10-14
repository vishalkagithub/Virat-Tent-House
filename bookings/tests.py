from datetime import date
from django.test import TestCase
from .models import Customer, Enquiry, Booking
from finance.models import Payment

class BookingsAndEnquiriesTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Mahesh Joshi',
            phone='+91 98290 12121',
            email='mahesh@example.com'
        )

    def test_enquiry_number_generation(self):
        enquiry = Enquiry.objects.create(
            customer_name='Sanjay Verma',
            phone='9829033333',
            event_type=Enquiry.EventType.WEDDING,
            event_date=date(2026, 12, 10),
            venue='Jaipur'
        )
        self.assertTrue(enquiry.enquiry_number.startswith('VTH-ENQ-'))
        self.assertIn(str(date.today().year), enquiry.enquiry_number)

    def test_booking_financials_and_payment_status(self):
        booking = Booking.objects.create(
            customer=self.customer,
            event_type='Wedding Reception',
            event_date=date(2026, 12, 15),
            venue='Clark Amer, Jaipur',
            total_amount=100000,
            discount=10000,
            status=Booking.Status.CONFIRMED
        )

        self.assertEqual(booking.final_amount, 90000)
        self.assertEqual(booking.total_paid, 0)
        self.assertEqual(booking.remaining_balance, 90000)
        self.assertEqual(booking.payment_status, 'Unpaid')

        # Record partial payment
        Payment.objects.create(
            booking=booking,
            amount=30000,
            payment_method=Payment.PaymentMethod.UPI
        )
        self.assertEqual(booking.total_paid, 30000)
        self.assertEqual(booking.remaining_balance, 60000)
        self.assertEqual(booking.payment_status, 'Partially Paid')

        # Record balance payment
        Payment.objects.create(
            booking=booking,
            amount=60000,
            payment_method=Payment.PaymentMethod.CASH
        )
        self.assertEqual(booking.total_paid, 90000)
        self.assertEqual(booking.remaining_balance, 0)
        self.assertEqual(booking.payment_status, 'Fully Paid')
