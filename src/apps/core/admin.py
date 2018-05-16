from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from apps.core.actions import export_as_csv_action
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
    list_display = ('course', 'status', 'group_id', 'user',
                    'get_class_time', 'sync_date',)
    readonly_fields = ('get_class_time',)
    search_fields = ('course', 'status', 'group_id', 'user',)
    list_filter = ('status', ('user', RelatedDropdownFilter),
                   ('sync_date', DateRangeFilter),)

    actions = [export_as_csv_action("CSV Export",
                                    fields=[('User', 'user'),
                                            ('Course', 'course'),
                                            ('Location', 'location'),
                                            ('Instructor', 'instructor'),
                                            ('Max students', 'max_students'),
                                            ('Status', 'status'),
                                            ('Sync date', 'sync_date'),
                                            ('Class time', 'get_class_time')])]

admin.site.register(EnrollWareGroup, AdminEnrollWareGroup)
