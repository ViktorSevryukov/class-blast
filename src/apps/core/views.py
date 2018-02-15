from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from apps.core.models import EnrollWareGroup, AHAField, EnrollClassTime
from apps.scraper.aha_importer import AHAImporter
from apps.scraper.scraper import ClassImporter
from apps.scraper.aha_exporter import AHAExporter

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
                importer = ClassImporter(
                    username='gentrain',
                    password='enrollware',
                    user=request.user
                )
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
                return redirect(reverse_lazy('dashboard:manage'))
                # return render(request, self.template_name, {
                #     'aha_form': form,
                #     'enroll_form': EnrollLoginForm()
                # })
        return render(request, self.template_name, {'form': form})


class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):

        ew_groups = EnrollWareGroup.objects.filter(user_id=request.user.id, synced=False)
        aha_fields = {field.type: field.value for field in AHAField.objects.all()}

        return render(request, self.template_name, {
            'ew_groups': ew_groups,
            'aha_fields': aha_fields
        })

    def post(self, request, *args, **kwargs):
        class_time = EnrollClassTime.objects.filter(group_id=request.POST['group_id']).first()
        print(request.POST['class_description'])
        group_data = {
        'course': request.POST['course'],
        'language': "English",
        'location': request.POST['location']+" ",
        'tc': request.POST['training_center'],
        'ts': request.POST['training_center'],
        'instructor': request.POST['instructor'],
        'date': class_time.date,
        'from': class_time.start,
        'to': class_time.end,
        'class_description': request.POST['class_description'],
        'roster_limit': request.POST['roster_limit'],
        'roster_date': request.POST['cutoff_date']
        }

        exporter = AHAExporter('jason.j.boudreault@gmail.com', 'Thecpr1', group_data)
        exporter.run()

        return render(request, self.template_name)

