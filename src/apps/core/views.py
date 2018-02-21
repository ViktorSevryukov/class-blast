from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.core.models import EnrollWareGroup, AHAField, EnrollClassTime, \
    EnrollWareCredentials, AHACredentials, Mapper
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

                return render( request, self.template_name, context)
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


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard.html'
    login_url = '/auth/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        ew_groups = EnrollWareGroup.objects.filter(
            user_id=request.user.id,
            synced=False
        )

        aha_fields = {field.type: field.value for field in AHAField.objects.all()}

        return render(request, self.template_name, {
            'ew_groups': ew_groups,
            'aha_fields': aha_fields
        })

    def post(self, request, *args, **kwargs):
        class_time = EnrollClassTime.objects.filter(
            group_id=request.POST['group_id']).first()

        aha_auth_data = AHACredentials.objects.filter(user=request.user).last()
        enroll_group = EnrollWareGroup.objects.filter(group_id=request.POST['group_id']).first()

        group_data = {
            'course': request.POST['course'],
            'language': "English",
            'location': request.POST['location'] + " ",
            'tc': request.POST['training_center'],
            'ts': request.POST['training_site'],
            'instructor': request.POST['instructor'],
            'date': class_time.date,
            'from': class_time.start,
            'to': class_time.end,
            'class_description': request.POST['class_description'],
            'roster_limit': request.POST['roster_limit'],
            'roster_date': request.POST['cutoff_date'],
            'class_notes': request.POST['class_notes']
        }

        #TODO: fix user literal

        MAPPER_FIELDS = (AHAField.FIELD_TYPES.COURSE, AHAField.FIELD_TYPES.LOCATION, AHAField.FIELD_TYPES.INSTRUCTOR)

        for field in MAPPER_FIELDS:

            Mapper.objects.update_or_create(
                aha_field=AHAField.objects.filter(type=field).first(),
                enroll_value=getattr(enroll_group, field),
                user=request.user,
                defaults={'aha_value': request.POST[field]}
            )

        exporter = AHAExporter(aha_auth_data.username, aha_auth_data.password, group_data)

        # TODO: handle error, show message
        exporter.run()

        return redirect(reverse_lazy('dashboard:manage'))


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
