from django.conf import settings
from .models import SystemSettings,Role

def system_settings(request):
    try:
        system_settings = SystemSettings.objects.first()  # Fetch your SystemSettings object
        # Fetch single role objects instead of QuerySet
        user_role2 = Role.objects.filter(id=2).first()
        user_role3 = Role.objects.filter(id=3).first()  # Fetch the role with ID 3
        user_role4 = Role.objects.filter(id=4).first()  # Fetch the role with ID 4
        # Initialize URLs to None
        fav_icon_url = None
        website_logo_url = None
        if system_settings:
            # Update with the correct fields from SystemSettings
            if system_settings.fav_icon:
                fav_icon_url = settings.MEDIA_URL + system_settings.fav_icon
            if system_settings.website_logo:
                website_logo_url = settings.MEDIA_URL + system_settings.website_logo

    except SystemSettings.DoesNotExist:
        system_settings = None

    return {
        'system_settings': system_settings,
        'user_role2': user_role2,
        'user_role3': user_role3,
        'user_role4': user_role4,
        'fav_icon': fav_icon_url,
        'website_logo': website_logo_url,
    }
