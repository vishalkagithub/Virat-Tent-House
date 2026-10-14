import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import BrandConfig, Notification
from accounts.models import StaffProfile
from services.models import ServiceCategory, Service, Package, PackageItem
from inventory.models import InventoryCategory, InventoryItem, InventoryTransaction, EventInventoryDispatch
from bookings.models import Customer, Enquiry, Booking, BookingItem, EventChecklist, StaffAssignment
from finance.models import Quotation, QuotationItem, Payment, Expense
from gallery.models import GalleryCategory, GalleryImage

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds realistic demo data for Virat Tent House'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Virat Tent House demo data seeding..."))

        # 1. Brand Configuration
        brand = BrandConfig.get_config()
        brand.business_name = "Virat Tent House"
        brand.tagline = "Premium Wedding Decor, Shamiana & Event Infrastructure"
        brand.phone_number = "+91 9453402167"
        brand.whatsapp_number = "919453402167"
        brand.email = "virattenthouse@gmail.com"
        brand.address = "Kurki Bazar, Akbarpur-Baskhari road, Ambedkar Nagar, UP, 224210"
        brand.google_maps_url = "https://maps.app.goo.gl/YhDC7fe9LJr8NqSCA"
        brand.google_maps_embed = "https://maps.google.com/maps?q=Kurki+Bazar,+Akbarpur-Baskhari+road,+Ambedkar+Nagar,+Uttar+Pradesh+224210&t=&z=14&ie=UTF8&iwloc=&output=embed"
        brand.working_hours = "Monday - Sunday: 8:00 AM - 10:00 PM"
        brand.save()
        self.stdout.write("  [+] Brand configuration updated.")

        # 2. Users & Roles
        # Super Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Super',
                'email': 'admin@virattenthouse.com',
                'role': User.Role.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone': '+91 98290 11111'
            }
        )
        admin_user.set_password('adminpassword123')
        admin_user.save()

        # Business Owner
        owner_user, _ = User.objects.get_or_create(
            username='virat_owner',
            defaults={
                'first_name': 'Virat',
                'last_name': 'Singh',
                'email': 'owner@virattenthouse.com',
                'role': User.Role.OWNER,
                'is_staff': True,
                'phone': '+91 98290 22222'
            }
        )
        owner_user.set_password('ownerpassword123')
        owner_user.save()

        # Manager
        manager_user, _ = User.objects.get_or_create(
            username='rajesh_manager',
            defaults={
                'first_name': 'Rajesh',
                'last_name': 'Sharma',
                'email': 'manager@virattenthouse.com',
                'role': User.Role.MANAGER,
                'is_staff': True,
                'phone': '+91 98290 33333'
            }
        )
        manager_user.set_password('managerpassword123')
        manager_user.save()

        # Staff Members
        staff1, _ = User.objects.get_or_create(
            username='mukesh_supervisor',
            defaults={
                'first_name': 'Mukesh',
                'last_name': 'Verma',
                'email': 'mukesh@virattenthouse.com',
                'role': User.Role.STAFF,
                'phone': '+91 98290 44444'
            }
        )
        staff1.set_password('staffpassword123')
        staff1.save()
        StaffProfile.objects.get_or_create(
            user=staff1,
            defaults={
                'designation': 'Field Supervisor',
                'skills': 'German Hangar Setup, Trussing, Team Leadership',
                'salary': 35000,
                'joining_date': date(2022, 4, 1)
            }
        )

        staff2, _ = User.objects.get_or_create(
            username='sunil_electrician',
            defaults={
                'first_name': 'Sunil',
                'last_name': 'Kumar',
                'email': 'sunil@virattenthouse.com',
                'role': User.Role.STAFF,
                'phone': '+91 98290 55555'
            }
        )
        staff2.set_password('staffpassword123')
        staff2.save()
        StaffProfile.objects.get_or_create(
            user=staff2,
            defaults={
                'designation': 'Senior Electrician & Genset Operator',
                'skills': 'Truss Illumination, Silent Genset, Electrical Cabling',
                'salary': 28000,
                'joining_date': date(2023, 1, 15)
            }
        )

        # Demo Customer
        cust_user, _ = User.objects.get_or_create(
            username='amit_customer',
            defaults={
                'first_name': 'Amit',
                'last_name': 'Agarwal',
                'email': 'amit.agarwal@example.com',
                'role': User.Role.CUSTOMER,
                'phone': '+91 98290 77777',
                'address': 'B-12, Malviya Nagar, Jaipur'
            }
        )
        cust_user.set_password('customerpassword123')
        cust_user.save()
        Customer.objects.get_or_create(
            user=cust_user,
            defaults={
                'name': 'Amit Agarwal',
                'phone': '+91 98290 77777',
                'email': 'amit.agarwal@example.com',
                'address': 'B-12, Malviya Nagar, Jaipur',
                'city': 'Jaipur'
            }
        )
        self.stdout.write("  [+] Users created (admin, virat_owner, rajesh_manager, mukesh_supervisor, sunil_electrician, amit_customer).")

        # 3. Service Categories
        categories_data = [
            ("Wedding Tent & Shamiana", "wedding-tent", "bi-house-heart", "Waterproof German Hangars, waterproof pandals, and royal Rajasthani shamianas."),
            ("Royal Mandap Decoration", "mandap-decoration", "bi-gem", "Artisan carved wooden and fiber mandaps, floral domes, and sacred fire canopies."),
            ("Stage & Backdrop Setup", "stage-decoration", "bi-display", "Grand reception backdrops, floral archways, LED screen frames, and acrylic ramps."),
            ("Theme Lighting & Illumination", "lighting", "bi-lamp", "Crystal chandeliers, warm halogen flooding, LED par cans, and fairy light curtains."),
            ("Furniture & Seating", "furniture", "bi-chair", "Maharaja throne chairs, cushioned banquet chairs, velvet diwans, and VIP sofas."),
            ("Cooling & Power Backup", "cooling-power", "bi-lightning-charge", "Misting jumbo coolers, tower AC units, and 125 kVA silent diesel generators."),
            ("Entrance Gate & Pathways", "entrance-gate", "bi-signpost", "Welcome archways, floral passage drapes, candle lanterns, and red carpet runways."),
            ("Dining & Banquet Setup", "dining-setup", "bi-cup-hot", "Round dining tables, luxury damask table covers, buffet canopies, and chaffing setups.")
        ]

        cat_objs = {}
        for idx, (name, slug, icon, desc) in enumerate(categories_data, start=1):
            cat, _ = ServiceCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'description': desc, 'order': idx}
            )
            cat_objs[slug] = cat
        self.stdout.write("  [+] 8 Service Categories created.")

        # 4. Services
        services_data = [
            ("German Hangar Waterproof Tent (60x100 ft)", "german-hangar-60x100", "wedding-tent", Service.PricingType.FIXED, 75000, "Setup", True, "Sturdy aluminum German Hangar with fire-retardant waterproof white PVC roof, sidewall drapes, and central ventilation."),
            ("Traditional Rajasthani Royal Shamiana", "royal-shamiana", "wedding-tent", Service.PricingType.PER_SQFT, 25, "Sq Ft", True, "Hand-block printed Marwari tent cloth with golden borders, bamboo structure, and vibrant ceiling draping."),
            ("Carved Royal Mandap with Fresh Floral Arch", "carved-royal-mandap", "mandap-decoration", Service.PricingType.FIXED, 45000, "Setup", True, "Fiberglass carved pillar mandap with dome, rose-marigold floral drapes, 4 chowki sets, and havan kund."),
            ("Pastel Floral Sangeet & Reception Stage", "reception-stage-pastel", "stage-decoration", Service.PricingType.FIXED, 35000, "Setup", True, "30x16 ft stage with carpet, pastel hydrangea-rose floral backdrop, neon light signage, and warm halo spots."),
            ("Crystal Chandelier & Ambient Lighting Package", "chandelier-lighting-pkg", "lighting", Service.PricingType.FIXED, 28000, "Package", True, "4 Grand imported crystal chandeliers, 24 warm white LED focus pars, and pathway fairy light canopy."),
            ("Maharaja Sofa & Throne Chairs (Set of 2)", "maharaja-sofa-set", "furniture", Service.PricingType.PER_ITEM, 3500, "Set / Day", False, "Gold carved teakwood high-back throne chairs with royal velvet upholstery for bride and groom."),
            ("Banquet Chairs with Spandex Cover & Ribbon", "banquet-chairs", "furniture", Service.PricingType.PER_ITEM, 45, "Chair / Day", False, "Heavy-gauge iron banquet chairs with padded seats, crisp white stretch covers, and satin gold sashes."),
            ("125 kVA Silent Generator with Fuel & Operator", "125kva-generator", "cooling-power", Service.PricingType.PER_DAY, 18000, "Day", True, "Soundproof diesel generator ensuring 100% uninterrupted power supply with on-site technician."),
            ("High-Pressure Outdoor Misting Fans", "misting-coolers", "cooling-power", Service.PricingType.PER_ITEM, 1500, "Unit / Day", False, "Heavy-duty outdoor water misting coolers ideal for summer day weddings and lunch banquets.")
        ]

        service_objs = {}
        for name, slug, cat_slug, p_type, price, unit, feat, desc in services_data:
            s, _ = Service.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': cat_objs[cat_slug],
                    'pricing_type': p_type,
                    'base_price': price,
                    'unit_name': unit,
                    'featured': feat,
                    'description': desc
                }
            )
            service_objs[slug] = s
        self.stdout.write("  [+] Core Services created.")

        # 5. Packages
        pkg_royal, _ = Package.objects.get_or_create(
            slug='royal-wedding-package',
            defaults={
                'name': 'Royal Maharaja Wedding Package',
                'starting_price': 250000,
                'description': 'The ultimate all-inclusive infrastructure for 800-1200 guests. Includes complete German Hangar waterproof tent, carved Mandap, reception stage, chandelier illumination, banquet seating, and dual genset backup.',
                'featured': True,
                'terms': 'Covers 2 full event days. In-city transport included. 30% advance required for date reservation.'
            }
        )
        # Package items
        PackageItem.objects.get_or_create(package=pkg_royal, service=service_objs['german-hangar-60x100'], defaults={'quantity': 1, 'notes': 'Main Hall'})
        PackageItem.objects.get_or_create(package=pkg_royal, service=service_objs['carved-royal-mandap'], defaults={'quantity': 1, 'notes': 'Mandap Lawn'})
        PackageItem.objects.get_or_create(package=pkg_royal, service=service_objs['reception-stage-pastel'], defaults={'quantity': 1, 'notes': 'Stage'})
        PackageItem.objects.get_or_create(package=pkg_royal, service=service_objs['chandelier-lighting-pkg'], defaults={'quantity': 2, 'notes': 'Full Canopy'})
        PackageItem.objects.get_or_create(package=pkg_royal, service=service_objs['125kva-generator'], defaults={'quantity': 1, 'notes': '24 Hours Power'})

        pkg_haldi, _ = Package.objects.get_or_create(
            slug='haldi-mehndi-carnival',
            defaults={
                'name': 'Vibrant Haldi & Mehndi Setup',
                'starting_price': 48000,
                'description': 'Bright yellow & marigold floral decor package with traditional Rajasthani shamiana, swing seating (Jhula), colorful umbrellas, and gadda seating.',
                'featured': True
            }
        )
        PackageItem.objects.get_or_create(package=pkg_haldi, service=service_objs['royal-shamiana'], defaults={'quantity': 1000, 'notes': 'Lawn Tent'})

        pkg_reception, _ = Package.objects.get_or_create(
            slug='grand-reception-package',
            defaults={
                'name': 'Grand Reception & Sangeet Package',
                'starting_price': 135000,
                'description': 'Complete setup featuring designer stage backdrop, acoustic sound trussing, ambient LED lighting, 400 banquet chairs, and VIP sofa lounge.',
                'featured': True
            }
        )
        self.stdout.write("  [+] Wedding Packages created.")

        # 6. Inventory Categories & Assets
        inv_cats = [
            ("Tents & Structural Fabric", "tents-fabric"),
            ("Chairs & Seating", "chairs-seating"),
            ("Tables & Dining", "tables-dining"),
            ("Stage & Mandap Structures", "stage-structures"),
            ("Lighting & Electricals", "lighting-electrical"),
            ("Cooling & Generators", "cooling-generators")
        ]
        inv_cat_objs = {}
        for name, slug in inv_cats:
            c, _ = InventoryCategory.objects.get_or_create(slug=slug, defaults={'name': name})
            inv_cat_objs[slug] = c

        inventory_items_data = [
            ("Iron Banquet Chairs (Padded)", "CHR-BNQ-001", "chairs-seating", 600, 580, 15, 5, "Pieces", 900, 40, "Heavy-duty square back banquet chairs"),
            ("Maharaja High-Back Gold Throne", "CHR-MAH-002", "chairs-seating", 12, 10, 2, 0, "Pieces", 15000, 1800, "Royal carved bride-groom chair"),
            ("3-Seater VIP Leatherette Sofa", "SOF-VIP-003", "chairs-seating", 40, 38, 2, 0, "Pieces", 8000, 800, "White Chesterfield 3-seater sofa"),
            ("German Hangar Aluminum Truss Section", "STR-TRU-001", "tents-fabric", 80, 80, 0, 0, "Sections", 22000, 1500, "Heavy-duty triangular aluminum trussing"),
            ("Waterproof White PVC Tent Fabric (20x20 ft)", "FAB-PVC-002", "tents-fabric", 150, 142, 6, 2, "Pieces", 4500, 450, "Heavy fire-retardant waterproof tent sheets"),
            ("Fiberglass Carved Mandap Pillars", "MAN-FIB-001", "stage-structures", 16, 16, 0, 0, "Pillars", 12000, 1200, "Ornate royal Rajasthani Mandap pillars"),
            ("Crystal Chandelier (8-Tier)", "LGT-CHN-001", "lighting-electrical", 10, 9, 1, 0, "Pieces", 18000, 2500, "Grand imported hanging chandeliers"),
            ("125 kVA Silent Generator Set", "GEN-125-001", "cooling-generators", 2, 2, 0, 0, "Sets", 650000, 18000, "Ashok Leyland acoustic silent diesel genset"),
            ("Heavy-Duty Outdoor Misting Fans", "COL-MST-001", "cooling-generators", 18, 16, 2, 0, "Units", 7500, 1200, "High pressure water misting jumbo fans"),
            ("Red Velvet Carpet Rolls (6x50 ft)", "CRP-RED-001", "stage-structures", 50, 45, 5, 0, "Rolls", 3200, 350, "Heavy plush red welcome runners")
        ]

        inv_objs = {}
        for name, sku, c_slug, total, ready, damaged, maint, unit, cost, rent, desc in inventory_items_data:
            item, _ = InventoryItem.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': inv_cat_objs[c_slug],
                    'total_quantity': total,
                    'available_quantity': ready,
                    'damaged_quantity': damaged,
                    'under_maintenance': maint,
                    'unit': unit,
                    'purchase_price': cost,
                    'rental_price': rent,
                    'description': desc
                }
            )
            inv_objs[sku] = item
        self.stdout.write("  [+] Physical Inventory assets created with real stock & damaged tracking.")

        # 7. Customers
        customer_records = [
            ("Vikram Singh Rathore", "+91 98290 88881", "vikram.rathore@example.com", "Civil Lines, Jaipur"),
            ("Sunita Meena", "+91 98290 88882", "sunita.meena@example.com", "Vaishali Nagar, Jaipur"),
            ("Pradeep Gupta", "+91 98290 88883", "pradeep.gupta@example.com", "Mansarovar, Jaipur"),
            ("Kavita Sharma", "+91 98290 88884", "kavita.sharma@example.com", "Raja Park, Jaipur")
        ]
        cust_objs = []
        for name, ph, em, addr in customer_records:
            c, _ = Customer.objects.get_or_create(
                phone=ph,
                defaults={'name': name, 'email': em, 'address': addr, 'city': 'Jaipur'}
            )
            cust_objs.append(c)

        # 8. Enquiries
        today = timezone.now().date()
        enq1, _ = Enquiry.objects.get_or_create(
            enquiry_number=f"VTH-ENQ-{today.year}-0001",
            defaults={
                'customer_name': 'Rameshwar Ji Agarwal',
                'phone': '+91 98290 99991',
                'whatsapp_number': '919829099991',
                'email': 'rameshwar.agarwal@example.com',
                'event_type': Enquiry.EventType.WEDDING,
                'event_date': today + timedelta(days=18),
                'venue': 'Celebration Gardens, Ajmer Road, Jaipur',
                'guest_count': 600,
                'required_services': 'Waterproof German Hangar, Floral Mandap, 400 Banquet Chairs, 20 VIP Sofas, 125 kVA Genset',
                'budget': 220000,
                'status': Enquiry.Status.NEW
            }
        )

        enq2, _ = Enquiry.objects.get_or_create(
            enquiry_number=f"VTH-ENQ-{today.year}-0002",
            defaults={
                'customer_name': 'Dharmendra Choudhary',
                'phone': '+91 98290 99992',
                'whatsapp_number': '919829099992',
                'email': 'dharmendra@example.com',
                'event_type': Enquiry.EventType.HALDI,
                'event_date': today + timedelta(days=7),
                'venue': 'Farmhouse 14, Sirsi Road, Jaipur',
                'guest_count': 250,
                'required_services': 'Yellow Haldi setup, shamiana, gadda seating, umbrellas',
                'budget': 45000,
                'status': Enquiry.Status.CONTACTED
            }
        )
        self.stdout.write("  [+] Sample Enquiries logged.")

        # 9. Confirmed Bookings
        bkg1, _ = Booking.objects.get_or_create(
            booking_id=f"VTH-BKG-{today.year}-0001",
            defaults={
                'customer': cust_objs[0], # Vikram Singh Rathore
                'event_type': 'Royal Rajput Wedding',
                'event_date': today + timedelta(days=12),
                'end_date': today + timedelta(days=13),
                'venue': 'Hotel Diggi Palace Grounds, Jaipur',
                'guest_count': 750,
                'total_amount': 240000,
                'discount': 10000,
                'advance_amount': 80000,
                'status': Booking.Status.CONFIRMED,
                'special_instructions': 'Royal maroon and gold theme. Mandap setup must be completed by 4 PM on wedding day.'
            }
        )
        # Booking Items
        BookingItem.objects.get_or_create(
            booking=bkg1,
            item_name="German Hangar Waterproof Tent (60x100 ft)",
            defaults={'service': service_objs['german-hangar-60x100'], 'quantity': 1, 'unit_price': 75000}
        )
        BookingItem.objects.get_or_create(
            booking=bkg1,
            item_name="Iron Banquet Chairs (Padded)",
            defaults={'inventory_item': inv_objs['CHR-BNQ-001'], 'quantity': 350, 'unit_price': 40}
        )
        BookingItem.objects.get_or_create(
            booking=bkg1,
            item_name="Carved Royal Mandap with Floral Arch",
            defaults={'service': service_objs['carved-royal-mandap'], 'quantity': 1, 'unit_price': 45000}
        )
        BookingItem.objects.get_or_create(
            booking=bkg1,
            item_name="125 kVA Silent Generator Set",
            defaults={'inventory_item': inv_objs['GEN-125-001'], 'quantity': 1, 'unit_price': 18000}
        )

        # Checklists for bkg1
        tasks = [
            ("German Hangar framework & trusses checked in warehouse", True),
            ("350 Banquet chairs loaded and inspected", True),
            ("Mandap fiber pillars packed with foam wrapping", False),
            ("125 kVA Silent generator fuel tank topped up", False),
            ("Lead supervisor and 10 workers assigned", True),
        ]
        for t_title, comp in tasks:
            EventChecklist.objects.get_or_create(
                booking=bkg1,
                title=t_title,
                defaults={'is_completed': comp, 'assigned_to': staff1 if comp else None}
            )

        # Staff assignment for bkg1
        StaffAssignment.objects.get_or_create(
            booking=bkg1,
            staff_member=staff1,
            role_in_event='Lead Event Supervisor'
        )
        StaffAssignment.objects.get_or_create(
            booking=bkg1,
            staff_member=staff2,
            role_in_event='Chief Electrical & Genset Operator'
        )

        # Booking 2 (Completed event)
        bkg2, _ = Booking.objects.get_or_create(
            booking_id=f"VTH-BKG-{today.year}-0002",
            defaults={
                'customer': cust_objs[1], # Sunita Meena
                'event_type': 'Wedding Reception & Sangeet',
                'event_date': today - timedelta(days=4),
                'venue': 'Shubh Labh Marriage Garden, Mansarovar',
                'guest_count': 450,
                'total_amount': 115000,
                'discount': 5000,
                'advance_amount': 50000,
                'status': Booking.Status.COMPLETED
            }
        )
        self.stdout.write("  [+] Bookings, checklist tasks, and staff assignments established.")

        # 10. Event Dispatches & Returns
        dispatch1, _ = EventInventoryDispatch.objects.get_or_create(
            booking=bkg2,
            item=inv_objs['CHR-BNQ-001'],
            defaults={
                'issued_quantity': 300,
                'returned_quantity': 295,
                'damaged_quantity': 3,
                'missing_quantity': 2,
                'status': EventInventoryDispatch.DispatchStatus.RETURNED,
                'notes': 'Returned to godown. 3 legs damaged during stage movement, 2 lost.'
            }
        )

        # 11. Quotation
        qtn1, _ = Quotation.objects.get_or_create(
            quotation_number=f"VTH-QTN-{today.year}-0001",
            defaults={
                'customer': cust_objs[0],
                'booking': bkg1,
                'event_type': 'Royal Rajput Wedding',
                'event_date': bkg1.event_date,
                'venue': bkg1.venue,
                'subtotal': 240000,
                'discount': 10000,
                'tax_rate': 0,
                'grand_total': 230000,
                'advance_required': 70000,
                'status': Quotation.Status.ACCEPTED
            }
        )
        QuotationItem.objects.get_or_create(quotation=qtn1, description="German Hangar 60x100 ft Waterproof Structure", defaults={'quantity': 1, 'unit_price': 75000, 'total_price': 75000})
        QuotationItem.objects.get_or_create(quotation=qtn1, description="Carved Royal Mandap with Fresh Roses & Marigold Arch", defaults={'quantity': 1, 'unit_price': 45000, 'total_price': 45000})
        QuotationItem.objects.get_or_create(quotation=qtn1, description="Banquet Chairs with White Stretch Covers (350 nos)", defaults={'quantity': 350, 'unit_price': 40, 'total_price': 14000})
        QuotationItem.objects.get_or_create(quotation=qtn1, description="Crystal Chandelier & Ambient Par Can Lighting", defaults={'quantity': 1, 'unit_price': 28000, 'total_price': 28000})
        QuotationItem.objects.get_or_create(quotation=qtn1, description="125 kVA Silent Generator Backup (Diesel included)", defaults={'quantity': 1, 'unit_price': 18000, 'total_price': 18000})
        qtn1.calculate_totals()
        self.stdout.write("  [+] Quotation VTH-QTN-2026-0001 created.")

        # 12. Payments
        Payment.objects.get_or_create(
            booking=bkg1,
            amount=80000,
            payment_date=today - timedelta(days=5),
            defaults={
                'payment_method': Payment.PaymentMethod.UPI,
                'transaction_id': 'UPI-REF-9382103847',
                'notes': 'Advance booking confirmation deposit',
                'recorded_by': manager_user
            }
        )
        Payment.objects.get_or_create(
            booking=bkg2,
            amount=50000,
            payment_date=today - timedelta(days=10),
            defaults={
                'payment_method': Payment.PaymentMethod.BANK_TRANSFER,
                'transaction_id': 'NEFT-SBIN2026049281',
                'notes': 'Advance payment',
                'recorded_by': manager_user
            }
        )
        Payment.objects.get_or_create(
            booking=bkg2,
            amount=60000,
            payment_date=today - timedelta(days=2),
            defaults={
                'payment_method': Payment.PaymentMethod.CASH,
                'transaction_id': 'CASH-VOUCHER-082',
                'notes': 'Final balance settlement on teardown',
                'recorded_by': manager_user
            }
        )
        self.stdout.write("  [+] Payments recorded.")

        # 13. Expenses
        Expense.objects.get_or_create(
            title="Diesel for 125 kVA Genset and Transport Truck",
            amount=8500,
            expense_date=today - timedelta(days=3),
            defaults={
                'category': Expense.Category.TRANSPORT,
                'related_booking': bkg2,
                'description': 'HP Petrol Pump, Jaipur. 95 Litres diesel',
                'added_by': manager_user
            }
        )
        Expense.objects.get_or_create(
            title="Field Setup Labour Wages (12 Workers x 2 Days)",
            amount=14400,
            expense_date=today - timedelta(days=2),
            defaults={
                'category': Expense.Category.LABOUR,
                'related_booking': bkg2,
                'description': 'Wages paid in cash for loading, installation, and dismantling',
                'added_by': manager_user
            }
        )
        Expense.objects.get_or_create(
            title="Welding & Structural Repair for Bent Chair Frames",
            amount=3200,
            expense_date=today - timedelta(days=1),
            defaults={
                'category': Expense.Category.REPAIR,
                'description': 'Repaired 10 iron chair frames and 2 truss clamps',
                'added_by': manager_user
            }
        )
        self.stdout.write("  [+] Expenses recorded.")

        # 14. Gallery
        gallery_cats = [
            ("Royal Weddings", "royal-weddings"),
            ("Artisan Mandaps", "artisan-mandaps"),
            ("Theme Lighting", "theme-lighting"),
            ("Stage & Backdrops", "stage-backdrops")
        ]
        for name, slug in gallery_cats:
            g_cat, _ = GalleryCategory.objects.get_or_create(slug=slug, defaults={'name': name})
            GalleryImage.objects.get_or_create(
                category=g_cat,
                title=f"Royal {name} Showcase at Diggi Palace",
                defaults={
                    'description': 'Majestic setup designed and executed by Virat Tent House Jaipur.',
                    'is_featured': True
                }
            )
        self.stdout.write("  [+] Gallery showcase created.")

        # 15. In-App Notifications
        Notification.objects.get_or_create(
            title="New Event Booking Confirmed",
            message=f"Booking #{bkg1.booking_id} for Vikram Singh Rathore has been locked for {bkg1.event_date}.",
            notification_type=Notification.NotificationType.BOOKING,
            link=f"/dashboard/bookings/{bkg1.id}/"
        )
        Notification.objects.get_or_create(
            title="Payment Received: ₹80,000",
            message=f"Advance deposit received for Booking #{bkg1.booking_id} via UPI.",
            notification_type=Notification.NotificationType.PAYMENT,
            link=f"/dashboard/bookings/{bkg1.id}/"
        )

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded complete realistic demo data for Virat Tent House!"))
        self.stdout.write(self.style.NOTICE(
            "Demo Credentials:\n"
            "  Admin:       username: admin           password: adminpassword123\n"
            "  Owner:       username: virat_owner     password: ownerpassword123\n"
            "  Manager:     username: rajesh_manager  password: managerpassword123\n"
            "  Staff:       username: mukesh_supervisor password: staffpassword123\n"
            "  Customer:    username: amit_customer   password: customerpassword123\n"
        ))
