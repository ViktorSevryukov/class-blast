from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from apps.auth_core.models import User
from apps.core.forms import AHALoginForm, EnrollLoginForm
from apps.core.models import EnrollWareGroup, AHAField, \
    EnrollWareCredentials, AHACredentials
from apps.core.tasks import import_enroll_groups, update_enroll_credentials, \
    import_aha_fields, update_aha_credentials
from celery import chain
from scraper.aha.importer import AHAImporter
from scraper.enrollware.importer import ClassImporter

import logging

logger = logging.getLogger('aha_export')


class ServicesLoginView(LoginRequiredMixin, View):
    template_name = 'services_login.html'

    TEST_MODE = False

    def get(self, request, *args, **kwargs):
        enroll_form = EnrollLoginForm()
        aha_form = AHALoginForm()
        return render(request, self.template_name,
                      {'enroll_form': enroll_form, 'aha_form': aha_form})

    # TODO: redirect in case both forms are filled, check another form filled then you are fill the one
    def post(self, request, *args, **kwargs):
        service_type = request.POST["service_type"]
        if service_type == "enroll":
            form = EnrollLoginForm(request.POST)
        else:
            form = AHALoginForm(request.POST)

        if form.is_valid():

            if service_type == "enroll":
                # TODO: hide real user data
                username = 'gentrain' if self.TEST_MODE else request.POST[
                    'username']
                password = 'enrollware' if self.TEST_MODE else request.POST[
                    'password']

                context = {
                    'enroll_form': form,
                    'aha_form': AHALoginForm(),
                    'success_auth': False
                }

                res = chain(
                    import_enroll_groups.s(username, password,
                                           request.user.id),
                    update_enroll_credentials.s()
                )()

                try:
                    res.parent.get()
                    context['success_auth'] = True
                except:
                    if res.parent.failed():
                        context['enrollware_error_message'] = \
                            "Sorry, your login data wrong, please try again"

                return render(request, self.template_name, context)
            else:
                username = 'jason.j.boudreault@gmail.com' if self.TEST_MODE else \
                request.POST['username']
                password = 'Thecpr1' if self.TEST_MODE else request.POST[
                    'password']
                # TODO: hide real user data
                res = chain(
                    import_aha_fields.s(username, password, request.user.id),
                    update_aha_credentials.s()
                )()

                try:
                    res.parent.get()
                except:
                    return render(request, self.template_name, {
                        'aha_error_message': "Sorry, your login data wrong, please try again",
                        'aha_form': form,
                        'enroll_form': EnrollLoginForm()
                    })

                return redirect(reverse_lazy('dashboard:manage'))
        return render(request, self.template_name, {'form': form})


class DashboardView(LoginRequiredMixin, ListView):
    model = EnrollWareGroup
    template_name = 'dashboard.html'
    context_object_name = 'ew_groups'
    paginate_by = 10
    login_url = '/auth/login/'
    redirect_field_name = ''

    def get_queryset(self):
        qs = self.model.objects.filter(
            Q(status=EnrollWareGroup.STATUS_CHOICES.UNSYNCED) | Q(
                status=EnrollWareGroup.STATUS_CHOICES.ERROR),
            user_id=self.request.user.id,
        ).order_by('-modified')
        return qs

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        aha_fields = {field.type: field.value for field in
                      self.request.user.aha_fields.all()}
        context['aha_fields'] = aha_fields
        return context


class SyncView(LoginRequiredMixin, View):
    login_url = '/auth/login/'
    redirect_field_name = ''
    template_name = 'dashboard.html'

    def post(self, request):
        credentials = request.user.enrollwarecredentials.first()

        if credentials:
            username = credentials.username
            password = credentials.password
            importer = ClassImporter(username, password, request.user)
            importer.run()

        return redirect(reverse_lazy('dashboard:manage'))
