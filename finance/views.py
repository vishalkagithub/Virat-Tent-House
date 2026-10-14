from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Quotation, QuotationItem, Payment, Expense
from .forms import QuotationForm, QuotationItemForm, PaymentForm, ExpenseForm
from .pdf_generator import generate_quotation_pdf
from bookings.models import Booking, Enquiry
from core.models import BrandConfig, Notification
from accounts.permissions import staff_required, manager_required

# Quotation Views
@login_required
@staff_required
def quotation_list(request):
    quotations = Quotation.objects.select_related('customer').all()
    status_filter = request.GET.get('status')
    search = request.GET.get('q', '').strip()

    if status_filter:
        quotations = quotations.filter(status=status_filter)
    if search:
        quotations = quotations.filter(
            Q(quotation_number__icontains=search) |
            Q(customer__name__icontains=search) |
            Q(customer__phone__icontains=search) |
            Q(venue__icontains=search)
        )

    context = {
        'quotations': quotations,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'finance/quotation_list.html', context)

@login_required
@manager_required
def quotation_create(request):
    booking_id = request.GET.get('booking_id')
    enquiry_id = request.GET.get('enquiry_id')
    initial_data = {}

    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
        initial_data = {
            'customer': booking.customer,
            'booking': booking,
            'event_type': booking.event_type,
            'event_date': booking.event_date,
            'venue': booking.venue,
            'subtotal': booking.total_amount,
            'discount': booking.discount,
        }
    elif enquiry_id:
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        from bookings.models import Customer
        cust, _ = Customer.objects.get_or_create(phone=enquiry.phone, defaults={'name': enquiry.customer_name})
        initial_data = {
            'customer': cust,
            'event_type': enquiry.get_event_type_display(),
            'event_date': enquiry.event_date,
            'venue': enquiry.venue,
            'subtotal': enquiry.budget or 0,
        }

    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            quotation = form.save()
            quotation.calculate_totals()
            messages.success(request, f"Quotation {quotation.quotation_number} generated.")
            return redirect('finance:quotation_detail', pk=quotation.id)
    else:
        form = QuotationForm(initial=initial_data)

    return render(request, 'finance/quotation_form.html', {'form': form, 'title': 'Generate Quotation'})

@login_required
@staff_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation.objects.select_related('customer', 'booking'), pk=pk)
    items = quotation.items.all().select_related('service')
    item_form = QuotationItemForm()

    if request.method == 'POST' and 'update_status' in request.POST:
        new_status = request.POST.get('status')
        if new_status in dict(Quotation.Status.choices):
            quotation.status = new_status
            quotation.save(update_fields=['status'])
            messages.success(request, f"Quotation status updated to {quotation.get_status_display()}.")
            return redirect('finance:quotation_detail', pk=pk)

    context = {
        'quotation': quotation,
        'items': items,
        'item_form': item_form,
    }
    return render(request, 'finance/quotation_detail.html', context)

@login_required
@manager_required
def quotation_add_item(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == 'POST':
        form = QuotationItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.quotation = quotation
            item.save()
            quotation.calculate_totals()
            messages.success(request, f"Added '{item.description}' to quotation.")
    return redirect('finance:quotation_detail', pk=pk)

def quotation_download_pdf(request, pk):
    quotation = get_object_or_404(Quotation.objects.select_related('customer', 'booking'), pk=pk)
    # Check permissions: staff or logged in customer matching quotation
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.is_customer:
        if not hasattr(request.user, 'customer_profile') or quotation.customer != request.user.customer_profile:
            messages.error(request, "Permission denied.")
            return redirect('accounts:customer_portal')

    brand = BrandConfig.get_config()
    pdf_buffer = generate_quotation_pdf(quotation, brand)
    filename = f"Quotation_{quotation.quotation_number}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

# Payment Views
@login_required
@staff_required
def payment_list(request):
    payments = Payment.objects.select_related('booking', 'booking__customer').all()
    search = request.GET.get('q', '').strip()
    method = request.GET.get('method')

    if method:
        payments = payments.filter(payment_method=method)
    if search:
        payments = payments.filter(
            Q(booking__booking_id__icontains=search) |
            Q(booking__customer__name__icontains=search) |
            Q(transaction_id__icontains=search)
        )

    context = {
        'payments': payments,
        'search': search,
        'method': method,
    }
    return render(request, 'finance/payment_list.html', context)

@login_required
@manager_required
def payment_create(request):
    booking_id = request.GET.get('booking_id')
    initial_data = {}
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
        initial_data = {
            'booking': booking,
            'amount': booking.remaining_balance,
        }

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.recorded_by = request.user
            payment.save()

            # Create notification
            Notification.objects.create(
                title=f"Payment Received: ₹{payment.amount:,.2f}",
                message=f"Received ₹{payment.amount:,.2f} for {payment.booking.booking_id} via {payment.get_payment_method_display()}.",
                notification_type=Notification.NotificationType.PAYMENT,
                link=f"/dashboard/bookings/{payment.booking.id}/"
            )

            messages.success(request, f"Payment of ₹{payment.amount:,.2f} recorded for {payment.booking.booking_id}.")
            return redirect('finance:payment_list')
    else:
        form = PaymentForm(initial=initial_data)

    return render(request, 'finance/payment_form.html', {'form': form, 'title': 'Record Customer Payment'})

# Expense Views
@login_required
@staff_required
def expense_list(request):
    expenses = Expense.objects.select_related('related_booking', 'added_by').all()
    category = request.GET.get('category')
    search = request.GET.get('q', '').strip()

    if category:
        expenses = expenses.filter(category=category)
    if search:
        expenses = expenses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'category': category,
        'search': search,
        'total_expense': total_expense,
    }
    return render(request, 'finance/expense_list.html', context)

@login_required
@manager_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.added_by = request.user
            expense.save()
            messages.success(request, f"Expense '{expense.title}' of ₹{expense.amount:,.2f} recorded.")
            return redirect('finance:expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'Record Business Expense'})
