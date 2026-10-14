from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet, PackageViewSet, CustomerViewSet,
    EnquiryViewSet, BookingViewSet, InventoryItemViewSet
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='api-service')
router.register(r'packages', PackageViewSet, basename='api-package')
router.register(r'customers', CustomerViewSet, basename='api-customer')
router.register(r'enquiries', EnquiryViewSet, basename='api-enquiry')
router.register(r'bookings', BookingViewSet, basename='api-booking')
router.register(r'inventory', InventoryItemViewSet, basename='api-inventory')

urlpatterns = [
    path('', include(router.urls)),
]
