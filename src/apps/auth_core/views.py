from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import resolve_url
from django.urls import reverse_lazy

import settings


class LoginView(BaseLoginView):
    template_name = 'login.html'

    def get_success_url(self):
        url = self.get_redirect_url()
        if self.request.user.has_services_credentials():
            return url or reverse_lazy('dashboard:manage')
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)
