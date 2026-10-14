from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from services.models import Service, Package
from bookings.models import Enquiry, Booking, Customer
from inventory.models import InventoryItem
from .serializers import (
    ServiceSerializer, PackageSerializer, CustomerSerializer,
    EnquirySerializer, BookingSerializer, InventoryItemSerializer
)

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True).select_related('category')
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'featured', 'pricing_type']
    search_fields = ['name', 'description']


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'phone', 'email']


class EnquiryViewSet(viewsets.ModelViewSet):
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'event_type', 'event_date']
    search_fields = ['customer_name', 'phone', 'enquiry_number', 'venue']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('customer', 'package').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'event_date']
    search_fields = ['booking_id', 'customer__name', 'venue']


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related('category').all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku']
