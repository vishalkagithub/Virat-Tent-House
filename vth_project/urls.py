from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from services import views as service_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('', include('accounts.urls', namespace='accounts')),
    path('services/', include('services.urls', namespace='services')),
    path('packages/', service_views.package_list, name='package_list_clean'),
    path('packages/<slug:slug>/', service_views.package_detail, name='package_detail_clean'),
    path('', include('bookings.urls', namespace='bookings')),
    path('', include('inventory.urls', namespace='inventory')),
    path('', include('finance.urls', namespace='finance')),
    path('', include('gallery.urls', namespace='gallery')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize Admin Header for Virat Tent House
admin.site.site_header = "Virat Tent House Management Portal"
admin.site.site_title = "Virat Tent House Admin"
admin.site.index_title = "Welcome to Virat Tent House Operations & ERP"
