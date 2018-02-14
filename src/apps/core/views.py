from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from apps.scraper.aha_importer import AHAImporter
from apps.scraper.scraper import ClassImporter

from .forms import AHALoginForm, EnrollLoginForm


class ServicesLoginView(View):
    template_name = 'services_login.html'

    def get(self, request, *args, **kwargs):
        enroll_form = EnrollLoginForm()
        aha_form = AHALoginForm()
        return render(request, self.template_name, {'enroll_form': enroll_form, 'aha_form': aha_form})

    #TODO: redirect in case both forms are filled, check another form filled then you are fill the one
    def post(self, request, *args, **kwargs):
        service_type = request.POST["service_type"]
        if service_type == "enroll":
            form = EnrollLoginForm(request.POST)
        else:
            form = AHALoginForm(request.POST)

        if form.is_valid():
            if service_type == "enroll":
                importer = ClassImporter('gentrain', 'enrollware')
                importer.run()
                #TODO: scraper turn on, we should return both of forms
                return render(request, self.template_name, {
                    'enroll_form': form,
                    'aha_form': AHALoginForm()
                })
            else:
                #TODO: aha_importer turn on
                importer = AHAImporter('jason.j.boudreault@gmail.com', 'Thecpr1')
                importer.run()
                return redirect(reverse_lazy('dashboard:dashboard'))
                # return render(request, self.template_name, {
                #     'aha_form': form,
                #     'enroll_form': EnrollLoginForm()
                # })
        return render(request, self.template_name, {'form': form})


class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
