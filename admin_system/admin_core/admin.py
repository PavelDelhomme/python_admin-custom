from django.contrib import admin
#from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


from django.urls import path
from .views import dashboard_view



class OutstandingTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'jti', 'created_at', 'expires_at', 'blacklisted')
    search_fields = ('user__username',)


class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'blacklisted_at')
    search_fields = ('token__user__username',)

class CustomAdminSite(admin.AdminSite):
    site_header = "Mon Administration Personnalisée"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(dashboard_view), name="dashboard"),
        ]
        return custom_urls + urls

admin_site = CustomAdminSite(name='custom_admin')

#admin.site.register(OutstandingToken, OutstandingTokenAdmin)
#admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
