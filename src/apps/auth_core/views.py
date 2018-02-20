from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import resolve_url
from django.urls import reverse_lazy

import settings
from apps.core.models import AHACredentials, EnrollWareCredentials


class LoginView(BaseLoginView):
    template_name = 'login.html'

    def get_success_url(self):
        aha_data_exist = AHACredentials.objects.filter(user=self.request.user).exists()
        enrollware_data_exist = EnrollWareCredentials.objects.filter(user=self.request.user).exists()
        url = self.get_redirect_url()

        if aha_data_exist and enrollware_data_exist:
            return url or reverse_lazy('dashboard:manage')

        return url or resolve_url(settings.LOGIN_REDIRECT_URL)