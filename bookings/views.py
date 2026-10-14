from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date

from .models import Enquiry, Booking, BookingItem, EventChecklist, StaffAssignment, Customer
from .forms import CustomerEnquiryForm, BookingForm, BookingItemForm, StaffAssignmentForm
from accounts.permissions import staff_required, manager_required
from core.models import Notification, BrandConfig

# Public Enquiry Views
def enquiry_create(request):
    if request.method == 'POST':
        form = CustomerEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            # Create in-app notification for admin/staff
            Notification.objects.create(
                title=f"New Enquiry: {enquiry.enquiry_number}",
                message=f"{enquiry.customer_name} submitted an enquiry for {enquiry.get_event_type_display()} on {enquiry.event_date} ({enquiry.guest_count} guests).",
                notification_type=Notification.NotificationType.ENQUIRY,
                link=f"/dashboard/enquiries/{enquiry.id}/"
            )
            messages.success(request, f"Thank you! Your enquiry has been received. Your Enquiry ID is {enquiry.enquiry_number}.")
            return redirect('bookings:enquiry_success', pk=enquiry.id)
    else:
        # Prepopulate event type if passed in GET parameter
        initial_event = request.GET.get('event_type')
        form = CustomerEnquiryForm(initial={'event_type': initial_event} if initial_event else None)

    return render(request, 'bookings/enquiry_form.html', {'form': form})

def enquiry_success(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    brand = BrandConfig.get_config()
    
    # Pre-fill WhatsApp message text
    whatsapp_text = (
        f"Namaste Virat Tent House, I have submitted Enquiry #{enquiry.enquiry_number} "
        f"for {enquiry.get_event_type_display()} on {enquiry.event_date} at {enquiry.venue} "
        f"({enquiry.guest_count} guests). My name is {enquiry.customer_name}."
    )
    import urllib.parse
    whatsapp_url = f"https://wa.me/{brand.whatsapp_number}?text={urllib.parse.quote(whatsapp_text)}"

    return render(request, 'bookings/enquiry_success.html', {
        'enquiry': enquiry,
        'whatsapp_url': whatsapp_url
    })

# ERP Enquiry Management
@login_required
@staff_required
def enquiry_list(request):
    enquiries = Enquiry.objects.all()
    status_filter = request.GET.get('status')
    search = request.GET.get('q', '').strip()

    if status_filter:
        enquiries = enquiries.filter(status=status_filter)
    if search:
        enquiries = enquiries.filter(
            Q(customer_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(enquiry_number__icontains=search) |
            Q(venue__icontains=search)
        )

    context = {
        'enquiries': enquiries,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'bookings/enquiry_list.html', context)

@login_required
@staff_required
def enquiry_detail(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if request.method == 'POST' and 'update_status' in request.POST:
        new_status = request.POST.get('status')
        if new_status in dict(Enquiry.Status.choices):
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f"Enquiry status updated to {enquiry.get_status_display()}.")
            return redirect('bookings:enquiry_detail', pk=pk)

    return render(request, 'bookings/enquiry_detail.html', {'enquiry': enquiry})

@login_required
@manager_required
def convert_enquiry_to_booking(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    
    # Create or fetch customer
    customer, _ = Customer.objects.get_or_create(
        phone=enquiry.phone,
        defaults={
            'name': enquiry.customer_name,
            'whatsapp_number': enquiry.whatsapp_number,
            'email': enquiry.email,
            'address': enquiry.venue
        }
    )

    # Create Booking
    booking = Booking.objects.create(
        customer=customer,
        enquiry=enquiry,
        event_type=enquiry.get_event_type_display(),
        event_date=enquiry.event_date,
        start_time=enquiry.start_time,
        end_time=enquiry.end_time,
        venue=enquiry.venue,
        guest_count=enquiry.guest_count,
        special_instructions=f"Converted from enquiry {enquiry.enquiry_number}. Required: {enquiry.required_services}",
        total_amount=enquiry.budget or 0.00,
        status=Booking.Status.PENDING_CONFIRMATION
    )

    # Initialize standard event preparation checklists
    default_checklists = [
        "Tent fabric & Shamiana structure checked & ready",
        "Chairs and banquet table linen washed & loaded",
        "Stage fabrication & floral structure prepared",
        "Theme lighting, cables & distribution box tested",
        "Silent generator & backup fuel tank inspected",
        "Transport truck & loading team arranged",
        "Lead supervisor & electrician assigned",
        "Customer confirmation & venue access timing verified",
    ]
    for task in default_checklists:
        EventChecklist.objects.create(booking=booking, title=task)

    enquiry.status = Enquiry.Status.CONFIRMED
    enquiry.save()

    messages.success(request, f"Enquiry {enquiry.enquiry_number} successfully converted to Booking {booking.booking_id}!")
    return redirect('bookings:booking_detail', pk=booking.id)

# ERP Booking Management
@login_required
@staff_required
def booking_list(request):
    bookings = Booking.objects.select_related('customer').all()
    status_filter = request.GET.get('status')
    search = request.GET.get('q', '').strip()

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if search:
        bookings = bookings.filter(
            Q(booking_id__icontains=search) |
            Q(customer__name__icontains=search) |
            Q(customer__phone__icontains=search) |
            Q(venue__icontains=search)
        )

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'bookings/booking_list.html', context)

@login_required
@manager_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            customer, _ = Customer.objects.get_or_create(
                phone=form.cleaned_data['customer_phone'],
                defaults={
                    'name': form.cleaned_data['customer_name'],
                    'email': form.cleaned_data['customer_email'],
                    'address': form.cleaned_data['customer_address'],
                }
            )
            booking = form.save(commit=False)
            booking.customer = customer
            booking.save()

            # Initialize checklist
            for task in [
                "Tent & Pandal framework loaded",
                "Seating & Chairs verified",
                "Stage & Mandap decoration ready",
                "Sound & Lighting equipment packed",
                "Generator fuel tested",
                "Team dispatched to venue",
            ]:
                EventChecklist.objects.create(booking=booking, title=task)

            messages.success(request, f"Booking {booking.booking_id} created successfully!")
            return redirect('bookings:booking_detail', pk=booking.id)
    else:
        form = BookingForm()
    return render(request, 'bookings/booking_form.html', {'form': form, 'title': 'Create New Event Booking'})

@login_required
@staff_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('customer', 'package'), pk=pk)
    items = booking.items.all().select_related('service', 'inventory_item')
    checklist = booking.checklist_items.all()
    assignments = booking.staff_assignments.all().select_related('staff_member')
    payments = booking.payments.all()
    quotations = booking.quotations.all()
    dispatches = booking.dispatches.all().select_related('item')

    # Item Form
    item_form = BookingItemForm()
    staff_form = StaffAssignmentForm()

    if request.method == 'POST':
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(Booking.Status.choices):
                booking.status = new_status
                booking.save()
                messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
                return redirect('bookings:booking_detail', pk=pk)

    context = {
        'booking': booking,
        'items': items,
        'checklist': checklist,
        'assignments': assignments,
        'payments': payments,
        'quotations': quotations,
        'dispatches': dispatches,
        'item_form': item_form,
        'staff_form': staff_form,
    }
    return render(request, 'bookings/booking_detail.html', context)

@login_required
@manager_required
def booking_add_item(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.booking = booking
            item.save()

            # Automatically recalculate total amount
            total = sum(i.total_price for i in booking.items.all())
            booking.total_amount = total
            booking.save(update_fields=['total_amount'])

            messages.success(request, f"Added '{item.item_name}' to booking.")
    return redirect('bookings:booking_detail', pk=pk)

@login_required
@staff_required
def booking_toggle_checklist(request, pk, item_id):
    booking = get_object_or_404(Booking, pk=pk)
    checklist_item = get_object_or_404(EventChecklist, id=item_id, booking=booking)
    checklist_item.is_completed = not checklist_item.is_completed
    checklist_item.completed_at = timezone.now() if checklist_item.is_completed else None
    checklist_item.assigned_to = request.user
    checklist_item.save()
    status_str = "completed" if checklist_item.is_completed else "marked pending"
    messages.info(request, f"Task '{checklist_item.title}' {status_str}.")
    return redirect('bookings:booking_detail', pk=pk)

@login_required
@manager_required
def booking_add_staff(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = StaffAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.booking = booking
            assignment.save()
            messages.success(request, f"Assigned {assignment.staff_member.get_full_name()} as {assignment.role_in_event}.")
    return redirect('bookings:booking_detail', pk=pk)

# Event Calendar
@login_required
@staff_required
def calendar_view(request):
    bookings = Booking.objects.exclude(status='cancelled').select_related('customer')
    return render(request, 'bookings/calendar.html', {'bookings': bookings})
