from django.conf.urls import url

from apps.core.views import ServicesLoginView, DashboardView, SyncView

urlpatterns = [
    url(r'^manage/', DashboardView.as_view(), name='manage'),
    url(r'^services_login/$', ServicesLoginView.as_view(), name='services_login'),
    url(r'^sync/$', SyncView.as_view(), name='sync')
]
