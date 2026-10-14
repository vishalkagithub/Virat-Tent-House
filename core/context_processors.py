from .models import BrandConfig, Notification

def brand_context(request):
    """
    Exposes brand settings across all templates globally.
    """
    try:
        brand = BrandConfig.get_config()
    except Exception:
        # Fallback if database table not yet migrated
        brand = {
            'business_name': 'Virat Tent House',
            'tagline': 'Premium Wedding Decor, Shamiana & Event Infrastructure',
            'phone_number': '+91 9453402167',
            'whatsapp_number': '919453402167',
            'email': 'virattenthouse@gmail.com',
            'address': 'Kurki Bazar, Akbarpur-Baskhari road, Ambedkar Nagar, UP, 224210',
            'google_maps_url': 'https://maps.app.goo.gl/YhDC7fe9LJr8NqSCA',
            'google_maps_embed': 'https://maps.google.com/maps?q=Kurki+Bazar,+Akbarpur-Baskhari+road,+Ambedkar+Nagar,+Uttar+Pradesh+224210&t=&z=14&ie=UTF8&iwloc=&output=embed',
            'working_hours': 'Monday - Sunday: 8:00 AM - 10:00 PM',
            'facebook_url': 'https://facebook.com',
            'instagram_url': 'https://instagram.com',
            'youtube_url': 'https://youtube.com',
        }
    return {'brand': brand}

def notifications_context(request):
    """
    Provides unread notification counts and latest unread notifications for logged-in staff.
    """
    if request.user.is_authenticated and not request.user.is_customer:
        try:
            notifications = Notification.objects.filter(is_read=False)[:5]
            unread_count = Notification.objects.filter(is_read=False).count()
            return {
                'unread_notifications': notifications,
                'unread_notifications_count': unread_count,
            }
        except Exception:
            return {'unread_notifications': [], 'unread_notifications_count': 0}
    return {'unread_notifications': [], 'unread_notifications_count': 0}
