from django.conf.urls import url

from apps.core.views.api import export_group, check_tasks, ImportEnroll, \
    ImportAHA

urlpatterns = [
    url(r'^import/enroll/$', ImportEnroll.as_view(), name='import_enroll_groups'),
    url(r'^import/aha/$', ImportAHA.as_view(), name='import_aha_fields'),

    url(r'^export/$', export_group, name='export'),
    url(r'^check_tasks/$', check_tasks, name='check_tasks')
]
