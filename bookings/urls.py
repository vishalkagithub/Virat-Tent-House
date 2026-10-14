from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Public
    path('enquiry/', views.enquiry_create, name='enquiry_create'),
    path('enquiry/<int:pk>/confirmation/', views.enquiry_success, name='enquiry_success'),

    # ERP
    path('dashboard/enquiries/', views.enquiry_list, name='enquiry_list'),
    path('dashboard/enquiries/<int:pk>/', views.enquiry_detail, name='enquiry_detail'),
    path('dashboard/enquiries/<int:pk>/convert/', views.convert_enquiry_to_booking, name='convert_enquiry_to_booking'),

    path('dashboard/bookings/', views.booking_list, name='booking_list'),
    path('dashboard/bookings/create/', views.booking_create, name='booking_create'),
    path('dashboard/bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('dashboard/bookings/<int:pk>/add-item/', views.booking_add_item, name='booking_add_item'),
    path('dashboard/bookings/<int:pk>/checklist/<int:item_id>/toggle/', views.booking_toggle_checklist, name='booking_toggle_checklist'),
    path('dashboard/bookings/<int:pk>/assign-staff/', views.booking_add_staff, name='booking_add_staff'),

    path('dashboard/calendar/', views.calendar_view, name='calendar'),
]
