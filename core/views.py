from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from datetime import timedelta

from .models import BrandConfig, Notification
from accounts.permissions import staff_required, owner_required
from services.models import Service, Package, ServiceCategory
from bookings.models import Booking, Enquiry, Customer
from inventory.models import InventoryItem, EventInventoryDispatch
from finance.models import Payment, Expense, Quotation
from gallery.models import GalleryImage

def home(request):
    featured_services = Service.objects.filter(is_active=True, featured=True)[:6]
    all_categories = ServiceCategory.objects.filter(is_active=True)[:8]
    packages = Package.objects.filter(is_active=True)[:4]
    gallery_highlights = GalleryImage.objects.filter(is_featured=True)[:8]
    if not gallery_highlights.exists():
        gallery_highlights = GalleryImage.objects.all()[:8]

    context = {
        'featured_services': featured_services,
        'categories': all_categories,
        'packages': packages,
        'gallery_highlights': gallery_highlights,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

@login_required
@staff_required
def dashboard(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Bookings Stats
    todays_bookings = Booking.objects.filter(event_date=today)
    upcoming_events = Booking.objects.filter(
        event_date__gte=today,
        status__in=['confirmed', 'in_preparation', 'event_ongoing']
    ).order_by('event_date')[:6]

    total_bookings_count = Booking.objects.count()
    pending_enquiries_count = Enquiry.objects.filter(status='new').count()
    pending_quotations_count = Quotation.objects.filter(status__in=['draft', 'sent']).count()

    # Financial Stats (Monthly)
    monthly_revenue = Payment.objects.filter(
        payment_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    monthly_expenses = Expense.objects.filter(
        expense_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    estimated_profit = monthly_revenue - monthly_expenses

    # Total Outstanding Receivables (Pending balances on all confirmed/completed bookings)
    all_active_bookings = Booking.objects.exclude(status='cancelled')
    total_receivable = 0
    for bkg in all_active_bookings:
        total_receivable += bkg.remaining_balance

    # Inventory Alerts
    damaged_items = InventoryItem.objects.filter(damaged_quantity__gt=0)
    low_stock_items = InventoryItem.objects.filter(total_quantity__lte=20, is_active=True)

    # Recent Enquiries
    recent_enquiries = Enquiry.objects.order_by('-created_at')[:5]

    # Chart Data: Bookings by Event Type
    event_type_counts = Booking.objects.values('event_type').annotate(count=Count('id')).order_by('-count')[:5]
    chart_event_labels = [item['event_type'] for item in event_type_counts]
    chart_event_data = [item['count'] for item in event_type_counts]

    context = {
        'today': today,
        'todays_bookings': todays_bookings,
        'upcoming_events': upcoming_events,
        'total_bookings_count': total_bookings_count,
        'pending_enquiries_count': pending_enquiries_count,
        'pending_quotations_count': pending_quotations_count,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        'estimated_profit': estimated_profit,
        'total_receivable': total_receivable,
        'damaged_items': damaged_items,
        'low_stock_items': low_stock_items,
        'recent_enquiries': recent_enquiries,
        'chart_event_labels': chart_event_labels,
        'chart_event_data': chart_event_data,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@staff_required
def reports(request):
    today = timezone.now().date()
    start_of_year = today.replace(month=1, day=1)

    total_revenue_ytd = Payment.objects.filter(payment_date__gte=start_of_year).aggregate(total=Sum('amount'))['total'] or 0
    total_expense_ytd = Expense.objects.filter(expense_date__gte=start_of_year).aggregate(total=Sum('amount'))['total'] or 0
    net_profit_ytd = total_revenue_ytd - total_expense_ytd

    expenses_by_category = Expense.objects.values('category').annotate(total=Sum('amount')).order_by('-total')
    payments_by_method = Payment.objects.values('payment_method').annotate(total=Sum('amount')).order_by('-total')

    context = {
        'today': today,
        'total_revenue_ytd': total_revenue_ytd,
        'total_expense_ytd': total_expense_ytd,
        'net_profit_ytd': net_profit_ytd,
        'expenses_by_category': expenses_by_category,
        'payments_by_method': payments_by_method,
    }
    return render(request, 'core/reports.html', context)

@login_required
@staff_required
def notifications_view(request):
    notifications = Notification.objects.all()[:50]
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        Notification.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('core:notifications')

    return render(request, 'core/notifications.html', {'notifications': notifications})

@login_required
@owner_required
def brand_settings(request):
    config = BrandConfig.get_config()
    if request.method == 'POST':
        config.business_name = request.POST.get('business_name', config.business_name)
        config.tagline = request.POST.get('tagline', config.tagline)
        config.phone_number = request.POST.get('phone_number', config.phone_number)
        config.whatsapp_number = request.POST.get('whatsapp_number', config.whatsapp_number)
        config.email = request.POST.get('email', config.email)
        config.address = request.POST.get('address', config.address)
        config.google_maps_url = request.POST.get('google_maps_url', config.google_maps_url)
        config.google_maps_embed = request.POST.get('google_maps_embed', config.google_maps_embed)
        config.working_hours = request.POST.get('working_hours', config.working_hours)
        config.facebook_url = request.POST.get('facebook_url', config.facebook_url)
        config.instagram_url = request.POST.get('instagram_url', config.instagram_url)
        config.youtube_url = request.POST.get('youtube_url', config.youtube_url)
        if 'logo' in request.FILES:
            config.logo = request.FILES['logo']
        config.save()
        messages.success(request, "Brand configuration updated successfully.")
        return redirect('core:brand_settings')

    return render(request, 'core/brand_settings.html', {'config': config})

def robots_txt(request):
    content = "User-agent: *\nDisallow: /dashboard/\nDisallow: /admin/\nAllow: /\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://virattenthouse.com/</loc><priority>1.0</priority></url>
  <url><loc>https://virattenthouse.com/services/</loc><priority>0.8</priority></url>
  <url><loc>https://virattenthouse.com/packages/</loc><priority>0.8</priority></url>
  <url><loc>https://virattenthouse.com/gallery/</loc><priority>0.7</priority></url>
  <url><loc>https://virattenthouse.com/about/</loc><priority>0.6</priority></url>
  <url><loc>https://virattenthouse.com/contact/</loc><priority>0.7</priority></url>
  <url><loc>https://virattenthouse.com/enquiry/</loc><priority>0.9</priority></url>
</urlset>"""
    return HttpResponse(content, content_type="application/xml")
