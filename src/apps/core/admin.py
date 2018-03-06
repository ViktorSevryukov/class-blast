from django.contrib import admin
from .models import EnrollWareGroup, EnrollClassTime, EnrollWareCredentials, AHACredentials, Mapper, AHAField


admin.site.register(EnrollClassTime)
admin.site.register(EnrollWareCredentials)
admin.site.register(AHACredentials)
admin.site.register(Mapper)
admin.site.register(AHAField)


class AdminEnrollWareGroup(admin.ModelAdmin):
    list_display = ('course', 'status', 'group_id')
    search_fields = ('course', 'status', 'group_id')
admin.site.register(EnrollWareGroup, AdminEnrollWareGroup)
