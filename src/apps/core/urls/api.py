from django.conf.urls import url

from apps.core.views.api import export_group, check_tasks

urlpatterns = [
    url(r'^export/$', export_group, name='export'),
    url(r'^check_tasks/$', check_tasks, name='check_tasks')
]
