from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Package, ServiceCategory, PackageItem
from .forms import ServiceForm, PackageForm
from accounts.permissions import manager_required

# Public Catalog Views
def service_list(request):
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    selected_category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()

    services = Service.objects.filter(is_active=True)

    if selected_category_slug:
        services = services.filter(category__slug=selected_category_slug)
    if search_query:
        services = services.filter(name__icontains=search_query)

    context = {
        'categories': categories,
        'services': services,
        'selected_category_slug': selected_category_slug,
        'search_query': search_query,
    }
    return render(request, 'services/service_list.html', context)

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(category=service.category, is_active=True).exclude(id=service.id)[:4]
    return render(request, 'services/service_detail.html', {
        'service': service,
        'related_services': related_services
    })

def package_list(request):
    packages = Package.objects.filter(is_active=True).prefetch_related('items__service')
    return render(request, 'services/package_list.html', {'packages': packages})

def package_detail(request, slug):
    package = get_object_or_404(Package, slug=slug, is_active=True)
    other_packages = Package.objects.filter(is_active=True).exclude(id=package.id)[:3]
    return render(request, 'services/package_detail.html', {
        'package': package,
        'other_packages': other_packages
    })

# Admin Management Views
@login_required
@manager_required
def service_manage_list(request):
    services = Service.objects.all().select_related('category')
    return render(request, 'services/service_manage_list.html', {'services': services})

@login_required
@manager_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"Service '{service.name}' created successfully.")
            return redirect('services:service_manage_list')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Add New Service'})

@login_required
@manager_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service '{service.name}' updated successfully.")
            return redirect('services:service_manage_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'title': f'Edit Service: {service.name}'})

@login_required
@manager_required
def package_manage_list(request):
    packages = Package.objects.all().prefetch_related('items')
    return render(request, 'services/package_manage_list.html', {'packages': packages})

@login_required
@manager_required
def package_create(request):
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            messages.success(request, f"Package '{package.name}' created successfully.")
            return redirect('services:package_manage_list')
    else:
        form = PackageForm()
    return render(request, 'services/package_form.html', {'form': form, 'title': 'Create New Package'})
