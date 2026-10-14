from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/reports/', views.reports, name='reports'),
    path('dashboard/notifications/', views.notifications_view, name='notifications'),
    path('dashboard/brand-settings/', views.brand_settings, name='brand_settings'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
