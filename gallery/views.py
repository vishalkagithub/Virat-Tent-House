from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms

from .models import GalleryCategory, GalleryImage
from accounts.permissions import manager_required

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['category', 'title', 'image', 'description', 'is_featured']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

def gallery_list(request):
    categories = GalleryCategory.objects.all()
    selected_category = request.GET.get('category')
    images = GalleryImage.objects.select_related('category').all()

    if selected_category:
        images = images.filter(category__slug=selected_category)

    context = {
        'categories': categories,
        'images': images,
        'selected_category': selected_category,
    }
    return render(request, 'gallery/gallery_list.html', context)

@login_required
@manager_required
def gallery_manage_list(request):
    images = GalleryImage.objects.select_related('category').all()
    return render(request, 'gallery/gallery_manage_list.html', {'images': images})

@login_required
@manager_required
def gallery_create(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save()
            messages.success(request, f"Photo '{img.title}' uploaded successfully.")
            return redirect('gallery:gallery_manage_list')
    else:
        form = GalleryImageForm()
    return render(request, 'gallery/gallery_form.html', {'form': form, 'title': 'Upload Gallery Image'})
