from django.conf.urls import url
from django.contrib.auth import views as auth_views

from apps.auth_core.views import LoginView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout')
]
