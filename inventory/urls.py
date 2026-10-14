from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/inventory/', views.inventory_list, name='inventory_list'),
    path('dashboard/inventory/create/', views.inventory_create, name='inventory_create'),
    path('dashboard/inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),
    path('dashboard/inventory/availability/', views.check_availability, name='check_availability'),
    path('dashboard/inventory/dispatch/<int:booking_id>/', views.booking_dispatch_manage, name='booking_dispatch_manage'),
    path('dashboard/inventory/dispatch/return/<int:dispatch_id>/', views.dispatch_process_return, name='dispatch_process_return'),
]
