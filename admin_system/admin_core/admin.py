from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class OutstandingTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'jti', 'created_at', 'expires_at', 'blacklisted')
    search_fields = ('user__username',)


class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'blacklisted_at')
    search_fields = ('token__user__username',)


admin.site.register(OutstandingToken, OutstandingTokenAdmin)
admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
