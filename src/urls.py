from django.contrib import admin
from django.conf.urls import include, url

from apps.core.views import ServiceLoginView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url('^service_login/', ServiceLoginView.as_view()),
]

