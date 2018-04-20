from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from apps.core.filters import RelatedDropdownFilter
from .models import EnrollWareGroup, EnrollClassTime, EnrollWareCredentials, \
    AHACredentials, Mapper, AHAField, AHAGroup

admin.site.register(EnrollClassTime)
admin.site.register(EnrollWareCredentials)
admin.site.register(AHACredentials)
admin.site.register(Mapper)
admin.site.register(AHAField)
admin.site.register(AHAGroup)


class AdminEnrollWareGroup(admin.ModelAdmin):

    list_display = ('course', 'status', 'group_id', 'user', 'sync_date')
    search_fields = ('course', 'status', 'group_id', 'user')
    list_filter = ('status', ('user', RelatedDropdownFilter), ('sync_date', DateRangeFilter))

admin.site.register(EnrollWareGroup, AdminEnrollWareGroup)

