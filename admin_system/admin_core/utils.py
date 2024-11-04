from datetime import timedelta
from django.conf import settings
from .models import ProjectSetting

def get_jwt_settings():
    try:
        access_token_lifetime = timedelta(minutes=int(ProjectSetting.objects.get(key="ACCESS_TOKEN_LIFETIME").value))
        refresh_token_lifetime = timedelta(days=int(ProjectSetting.objects.get(key="REFRESH_TOKEN_LIFETIME").value))
        rotate_refresh_tokens = bool(ProjectSetting.objects.get(key="ROTATE_REFRESH_TOKENS").value == 'True')
    except ProjectSetting.DoesNotExist:
        # Valeurs par défaut si les paramètres ne sont pas encore définis
        access_token_lifetime = timedelta(minutes=5)
        refresh_token_lifetime = timedelta(days=1)
        rotate_refresh_tokens = False

    return {
        'ACCESS_TOKEN_LIFETIME': access_token_lifetime,
        'REFRESH_TOKEN_LIFETIME': refresh_token_lifetime,
        'ROTATE_REFRESH_TOKENS': rotate_refresh_tokens,
        'BLACKLIST_AFTER_ROTATION': True,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': settings.SECRET_KEY,
        'AUTH_HEADER_TYPES': ('Bearer',),
    }
