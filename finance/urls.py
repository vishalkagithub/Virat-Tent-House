from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Quotations
    path('dashboard/quotations/', views.quotation_list, name='quotation_list'),
    path('dashboard/quotations/create/', views.quotation_create, name='quotation_create'),
    path('dashboard/quotations/<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('dashboard/quotations/<int:pk>/add-item/', views.quotation_add_item, name='quotation_add_item'),
    path('dashboard/quotations/<int:pk>/pdf/', views.quotation_download_pdf, name='quotation_download_pdf'),

    # Payments
    path('dashboard/payments/', views.payment_list, name='payment_list'),
    path('dashboard/payments/create/', views.payment_create, name='payment_create'),

    # Expenses
    path('dashboard/expenses/', views.expense_list, name='expense_list'),
    path('dashboard/expenses/create/', views.expense_create, name='expense_create'),
]
