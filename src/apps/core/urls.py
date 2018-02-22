from django.conf.urls import url

from apps.core.views import ServicesLoginView, DashboardView, SyncView
from apps.core.api import export_group

urlpatterns = [
    url(r'^manage/', DashboardView.as_view(), name='manage'),
    url(r'^services_login/$', ServicesLoginView.as_view(), name='services_login'),
    url(r'^sync/$', SyncView.as_view(), name='sync'),
    url(r'^export/$', export_group, name='export')
]
