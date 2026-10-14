from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import InventoryCategory, InventoryItem, EventInventoryDispatch, InventoryTransaction
from bookings.models import Customer, Booking, BookingItem

User = get_user_model()

class InventoryAvailabilityAndDispatchTest(TestCase):
    def setUp(self):
        self.category = InventoryCategory.objects.create(name='Chairs & Seating', slug='chairs')
        self.chairs = InventoryItem.objects.create(
            category=self.category,
            name='Banquet Chairs',
            sku='CHR-BNQ-TEST',
            total_quantity=500,
            available_quantity=500,
            damaged_quantity=0,
            under_maintenance=0,
            unit='Pieces',
            rental_price=40
        )
        self.customer = Customer.objects.create(name='Rahul Sharma', phone='9829000000')

    def test_overlapping_booking_availability_and_shortage(self):
        test_date = date(2026, 11, 20)

        # Booking A: 300 chairs confirmed on 20 Nov
        booking_a = Booking.objects.create(
            customer=self.customer,
            event_type='Wedding',
            event_date=test_date,
            venue='Jaipur Lawn',
            status=Booking.Status.CONFIRMED
        )
        BookingItem.objects.create(
            booking=booking_a,
            inventory_item=self.chairs,
            item_name='Banquet Chairs',
            quantity=300,
            unit_price=40
        )

        # Now check availability for Booking B wanting 250 chairs on the same date
        result = self.chairs.check_availability(
            start_date=test_date,
            requested_quantity=250
        )

        self.assertEqual(result['total_stock'], 500)
        self.assertEqual(result['usable_stock'], 500)
        self.assertEqual(result['booked_quantity'], 300)
        self.assertEqual(result['available_for_date'], 200) # 500 - 300 = 200
        self.assertEqual(result['requested_quantity'], 250)
        self.assertEqual(result['shortage'], 50) # 250 requested - 200 available = 50 shortage
        self.assertFalse(result['is_available'])

        # Now check availability for a different date where no bookings exist
        different_date = date(2026, 11, 25)
        res_diff = self.chairs.check_availability(
            start_date=different_date,
            requested_quantity=250
        )
        self.assertEqual(res_diff['available_for_date'], 500)
        self.assertEqual(res_diff['shortage'], 0)
        self.assertTrue(res_diff['is_available'])

    def test_inventory_dispatch_and_return_adjustments(self):
        booking = Booking.objects.create(
            customer=self.customer,
            event_type='Reception',
            event_date=date(2026, 12, 1),
            venue='Royal Palace',
            status=Booking.Status.CONFIRMED
        )

        dispatch = EventInventoryDispatch.objects.create(
            booking=booking,
            item=self.chairs,
            issued_quantity=300,
            status=EventInventoryDispatch.DispatchStatus.DISPATCHED
        )

        # Process return: 295 returned good, 3 damaged, 2 missing
        dispatch.process_return(returned_qty=295, damaged_qty=3, missing_qty=2)

        self.chairs.refresh_from_db()
        self.assertEqual(dispatch.status, EventInventoryDispatch.DispatchStatus.RETURNED)
        self.assertEqual(dispatch.returned_quantity, 295)
        self.assertEqual(dispatch.damaged_quantity, 3)
        self.assertEqual(dispatch.missing_quantity, 2)

        # Verify damaged quantity increased on inventory item
        self.assertEqual(self.chairs.damaged_quantity, 3)
        # Verify total quantity reduced by missing count (500 - 2 = 498)
        self.assertEqual(self.chairs.total_quantity, 498)
