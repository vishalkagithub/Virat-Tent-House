from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import StaffProfile
from .forms import CustomerRegistrationForm, StaffCreationForm
from .permissions import manager_required, customer_required

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_customer:
            return redirect('accounts:customer_portal')
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if user.is_customer:
                return redirect('accounts:customer_portal')
            return redirect('core:dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('core:home')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Virat Tent House.")
            return redirect('accounts:customer_portal')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def customer_portal(request):
    if not request.user.is_customer:
        return redirect('core:dashboard')

    # Get or create customer profile
    from bookings.models import Customer, Booking, Enquiry
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'phone': request.user.phone,
            'email': request.user.email
        }
    )

    bookings = customer.bookings.all().order_by('-event_date')
    quotations = customer.quotations.all().order_by('-created_at')
    enquiries = Enquiry.objects.filter(phone=customer.phone).order_by('-created_at')

    context = {
        'customer': customer,
        'bookings': bookings,
        'quotations': quotations,
        'enquiries': enquiries,
    }
    return render(request, 'accounts/customer_portal.html', context)

@login_required
@manager_required
def staff_list(request):
    staff_members = User.objects.filter(role__in=[User.Role.STAFF, User.Role.MANAGER, User.Role.OWNER]).select_related('staff_profile')
    return render(request, 'accounts/staff_list.html', {'staff_members': staff_members})

@login_required
@manager_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                role=form.cleaned_data['role']
            )
            staff_profile = form.save(commit=False)
            staff_profile.user = user
            staff_profile.save()
            messages.success(request, f"Staff member '{user.get_full_name()}' registered successfully.")
            return redirect('accounts:staff_list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/staff_form.html', {'form': form})
