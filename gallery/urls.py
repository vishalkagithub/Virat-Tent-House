from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('dashboard/gallery/', views.gallery_manage_list, name='gallery_manage_list'),
    path('dashboard/gallery/create/', views.gallery_create, name='gallery_create'),
]
