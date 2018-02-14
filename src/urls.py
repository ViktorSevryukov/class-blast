from django.contrib import admin
from django.conf.urls import include, url


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('apps.auth_core.urls', namespace='auth')),
    url(r'^dashboard/', include('apps.core.urls', namespace='dashboard'))
]

