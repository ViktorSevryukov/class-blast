from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required

from apps.core.models import EnrollWareGroup, AHAField, EnrollClassTime, EnrollWareCredentials, AHACredentials
from scraper.aha.exporter import AHAExporter
from scraper.aha.importer import AHAImporter
from scraper.enrollware.importer import ClassImporter

from .forms import AHALoginForm, EnrollLoginForm


class ServicesLoginView(View):
    template_name = 'services_login.html'

    TEST_MODE = False

    def get(self, request, *args, **kwargs):
        enroll_form = EnrollLoginForm()
        aha_form = AHALoginForm()
        return render(request, self.template_name, {'enroll_form': enroll_form, 'aha_form': aha_form})

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

                EnrollWareCredentials.objects.update_or_create(username=username, user=request.user, defaults={'password': request.POST['password']})

                importer = ClassImporter(
                    username=username,
                    password=password,
                    user=request.user
                )
                importer.run()
                return render(request, self.template_name, {
                    'enroll_form': form,
                    'aha_form': AHALoginForm()
                })
            else:
                # TODO: hide real user data
                username = 'jason.j.boudreault@gmail.com' if self.TEST_MODE else request.POST['username']
                password = 'Thecpr1' if self.TEST_MODE else request.POST['password']

                AHACredentials.objects.update_or_create(username=username, user=request.user, defaults={'password': request.POST['password']})

                importer = AHAImporter(
                    username=username,
                    password=password
                )
                importer.run()
                return redirect(reverse_lazy('dashboard:manage'))

                # return render(request, self.template_name, {
                #     'aha_form': form,
                #     'enroll_form': EnrollLoginForm()
                # })
        return render(request, self.template_name, {'form': form})


# @login_required(login_url='/services_login/')
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
            'location': request.POST['location'] + " ",
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


class SyncView(View):
    template_name = 'dashboard.html'

    def post(self, request):
        credentials = request.user.enrollwarecredentials.first()

        if credentials:
            username = credentials.username
            password = credentials.password
            importer = ClassImporter(username, password, request.user)
            importer.run()

        return redirect(reverse_lazy('dashboard:manage'))


