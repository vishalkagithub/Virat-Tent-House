from rest_framework import serializers
from services.models import Service, Package, ServiceCategory
from bookings.models import Enquiry, Booking, Customer
from inventory.models import InventoryItem

class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_display = serializers.CharField(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'slug', 'category', 'category_name', 'pricing_type', 'base_price', 'unit_name', 'price_display', 'featured', 'description']


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'slug', 'description', 'starting_price', 'terms', 'featured']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'whatsapp_number', 'email', 'address', 'city']


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'


class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    ready_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = '__all__'
