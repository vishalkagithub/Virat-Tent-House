from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import InventoryItem, InventoryCategory, InventoryTransaction, EventInventoryDispatch
from .forms import InventoryItemForm, InventoryAvailabilityCheckForm, EventDispatchForm, EventReturnForm
from bookings.models import Booking
from accounts.permissions import staff_required, manager_required

@login_required
@staff_required
def inventory_list(request):
    items = InventoryItem.objects.select_related('category').all()
    categories = InventoryCategory.objects.all()
    selected_category = request.GET.get('category')
    search = request.GET.get('q', '').strip()

    if selected_category:
        items = items.filter(category__id=selected_category)
    if search:
        items = items.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(category__name__icontains=search)
        )

    context = {
        'items': items,
        'categories': categories,
        'selected_category': selected_category,
        'search': search,
    }
    return render(request, 'inventory/inventory_list.html', context)

@login_required
@manager_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            # Log purchase transaction
            InventoryTransaction.objects.create(
                item=item,
                transaction_type=InventoryTransaction.TransactionType.PURCHASE,
                quantity=item.total_quantity,
                notes="Initial stock intake upon item creation",
                created_by=request.user
            )
            messages.success(request, f"Item '{item.name}' added with SKU {item.sku}.")
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/inventory_form.html', {'form': form, 'title': 'Add New Inventory Asset'})

@login_required
@manager_required
def inventory_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Asset '{item.name}' updated successfully.")
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory/inventory_form.html', {'form': form, 'title': f'Edit Asset: {item.name}'})

@login_required
@staff_required
def check_availability(request):
    """
    Real-time inventory availability calculation considering overlapping bookings.
    Prevents double-booking and alerts on shortages!
    """
    result = None
    form = InventoryAvailabilityCheckForm(request.GET or None)
    if form.is_valid():
        item = form.cleaned_data['item']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date'] or start_date
        requested_qty = form.cleaned_data['requested_quantity']

        result = item.check_availability(
            start_date=start_date,
            end_date=end_date,
            requested_quantity=requested_qty
        )
        result['item_name'] = item.name
        result['unit'] = item.unit
        result['start_date'] = start_date
        result['end_date'] = end_date

    return render(request, 'inventory/check_availability.html', {
        'form': form,
        'result': result
    })

# Event Dispatch & Return Workflow
@login_required
@staff_required
def booking_dispatch_manage(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    dispatches = booking.dispatches.all().select_related('item')

    if request.method == 'POST' and 'add_dispatch' in request.POST:
        form = EventDispatchForm(request.POST)
        if form.is_valid():
            dispatch = form.save(commit=False)
            dispatch.booking = booking
            dispatch.dispatched_at = timezone.now()
            dispatch.save()
            messages.success(request, f"Added {dispatch.item.name} ({dispatch.issued_quantity} {dispatch.item.unit}) to event dispatch.")
            return redirect('inventory:booking_dispatch_manage', booking_id=booking.id)
    else:
        form = EventDispatchForm()

    return render(request, 'inventory/dispatch_manage.html', {
        'booking': booking,
        'dispatches': dispatches,
        'form': form
    })

@login_required
@staff_required
def dispatch_process_return(request, dispatch_id):
    dispatch = get_object_or_404(EventInventoryDispatch, id=dispatch_id)
    if request.method == 'POST':
        form = EventReturnForm(request.POST)
        if form.is_valid():
            ret_qty = form.cleaned_data['returned_quantity']
            dam_qty = form.cleaned_data['damaged_quantity']
            mis_qty = form.cleaned_data['missing_quantity']

            dispatch.process_return(
                returned_qty=ret_qty,
                damaged_qty=dam_qty,
                missing_qty=mis_qty,
                staff_user=request.user
            )

            messages.success(
                request,
                f"Return recorded for {dispatch.item.name}: {ret_qty} returned, {dam_qty} damaged, {mis_qty} missing."
            )
            return redirect('inventory:booking_dispatch_manage', booking_id=dispatch.booking.id)
    else:
        form = EventReturnForm(initial={
            'returned_quantity': dispatch.issued_quantity,
            'damaged_quantity': 0,
            'missing_quantity': 0
        })

    return render(request, 'inventory/return_form.html', {
        'dispatch': dispatch,
        'form': form
    })
