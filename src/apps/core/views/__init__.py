from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from apps.core.forms import AHALoginForm, EnrollLoginForm
from apps.core.models import EnrollWareGroup, AHAField, \
    EnrollWareCredentials, AHACredentials
from scraper.aha.importer import AHAImporter
from scraper.enrollware.importer import ClassImporter


import logging

logger = logging.getLogger('aha_export')


class ServicesLoginView(View):
    template_name = 'services_login.html'

    TEST_MODE = True

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
                username = 'gentrain' if self.TEST_MODE else request.POST['username']
                password = 'enrollware' if self.TEST_MODE else request.POST['password']

                context = {
                    'enroll_form': form,
                    'aha_form': AHALoginForm(),
                    'success_auth': False
                }

                importer = ClassImporter(
                    username=username,
                    password=password,
                    user=request.user
                )
                try:
                    importer.run()
                    context['success_auth'] = True
                except:
                    context['enrollware_error_message'] = \
                        "Sorry, your login data wrong, please try again"

                EnrollWareCredentials.objects.update_or_create(
                    username=username,
                    user=request.user,
                    defaults={'password': request.POST['password']}
                )

                return render(request, self.template_name, context)
            else:
                # TODO: hide real user data
                username = 'jason.j.boudreault@gmail.com' if self.TEST_MODE else request.POST['username']
                password = 'Thecpr1' if self.TEST_MODE else request.POST['password']

                importer = AHAImporter(
                    username=username,
                    password=password
                )

                try:
                    importer.run()
                except:
                    return render(request, self.template_name, {
                        'aha_error_message': "Sorry, your login data wrong, please try again",
                        'aha_form': form,
                        'enroll_form': EnrollLoginForm()
                    })

                AHACredentials.objects.update_or_create(
                    username=username,
                    user=request.user,
                    defaults={'password':request.POST['password']}
                )

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
            Q(status=EnrollWareGroup.STATUS_CHOICES.UNSYNCED) | Q(status=EnrollWareGroup.STATUS_CHOICES.ERROR),
            user_id=self.request.user.id,
        ).order_by('-modified')
        return qs

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        aha_fields = {field.type: field.value for field in AHAField.objects.all()}
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
