from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def root(request):
    # TODO: maybe simplify redirects
    if request.user.is_authenticated():
        if request.user.has_services_credentials():
            return redirect(reverse_lazy('dashboard:manage'))
        return redirect(reverse_lazy('dashboard:services_login'))
    return redirect(reverse_lazy('auth:login'))
