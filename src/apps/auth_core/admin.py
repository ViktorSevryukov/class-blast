from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _


from apps.auth_core.models import User


class UserAdmin(BaseUserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password', 'version')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'version', 'is_staff')

admin.site.register(User, UserAdmin)

