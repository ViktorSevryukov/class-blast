from django.contrib import admin

from apps.auth_core.models import User


class AdminUser(admin.ModelAdmin):
    fields = ('username', 'password', 'version', 'first_name', 'last_name', 'email',
              'is_superuser', 'is_staff', 'is_active', 'user_permissions', 'groups',
              'last_login', 'date_joined')
    list_display = ('__str__', 'version')
    search_fields = ('username', 'first_name', 'last_name')

admin.site.register(User, AdminUser)
