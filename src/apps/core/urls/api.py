from django.conf.urls import url

from apps.core.views.api import export_group, check_tasks, ImportEnroll

urlpatterns = [
    url(r'^import/$', ImportEnroll.as_view(), name='import_enroll_groups'),
    url(r'^export/$', export_group, name='export'),
    url(r'^check_tasks/$', check_tasks, name='check_tasks')
]
