from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Public
    path('', views.service_list, name='service_list'),
    path('packages/', views.package_list, name='package_list'),
    path('packages/<slug:slug>/', views.package_detail, name='package_detail'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),

    # Admin Management
    path('manage/all/', views.service_manage_list, name='service_manage_list'),
    path('manage/create/', views.service_create, name='service_create'),
    path('manage/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('manage/packages/all/', views.package_manage_list, name='package_manage_list'),
    path('manage/packages/create/', views.package_create, name='package_create'),
]
