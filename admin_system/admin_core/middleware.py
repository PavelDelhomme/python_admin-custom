from django.conf import settings
from .models import Setting
from .utils import get_jwt_settings

class LoadSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.load_settings()

    def __call__(self, request):
        return self.get_response(request)

    def load_settings(self):
        settings.SIMPLE_JWT = get_jwt_settings()
