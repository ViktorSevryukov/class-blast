import codecs
import csv
import io
import uuid
from datetime import datetime

import stripe
from django.conf import settings
from django.contrib import messages
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

logger = logging.getLogger('import_csv')


class ServicesLoginView(LoginRequiredMixin, View):
    """
    View for authorization on services from which data will be parsed
    """
    template_name = 'services_login.html'

    def get(self, request, *args, **kwargs):
        enroll_form = EnrollLoginForm()
        aha_form = AHALoginForm()

        context = {
            'enroll_form': enroll_form,
            'aha_form': aha_form,
            'success_auth': self.request.GET.get('success', False)
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        service_type = request.POST["service_type"]

        enroll_form = EnrollLoginForm(
            request.POST if service_type == 'enroll' else None)
        aha_form = AHALoginForm(
            request.POST if service_type == 'aha' else None)

        context = {
            'enroll_form': enroll_form,
            'aha_form': aha_form,
            'success_auth': False
        }

        if service_type == 'enroll' and enroll_form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            res = chain(
                import_enroll_groups.s(username, password,
                                       request.user.id),
                update_enroll_credentials.s()
            )()

            try:
                res.parent.get()
                context['success_auth'] = True
            except Exception as msg:
                if res.parent.failed():
                    context['enrollware_error_message'] = msg

            return render(request, self.template_name, context)

        if service_type == 'aha':
            if aha_form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                res = chain(
                    import_aha_fields.s(username, password, request.user.id),
                    update_aha_credentials.s()
                )()

                try:
                    res.parent.get()
                except Exception as msg:
                    context['aha_error_message'] = msg
                    context['success_auth'] = True
                    return render(request, self.template_name, context)
                return redirect(reverse_lazy('dashboard:manage'))
            else:
                context['success_auth'] = True
                return render(request, self.template_name, context)

        if service_type == 'skip':
            context['success_auth'] = True
            return render(request, self.template_name, context)

        return render(request, self.template_name, context)


class DashboardView(LoginRequiredMixin, ListView):
    """
    Main page for working with classes list
    """
    model = EnrollWareGroup
    template_name = 'dashboard.html'
    context_object_name = 'ew_groups'
    paginate_by = 10
    login_url = '/auth/login/'
    redirect_field_name = ''

    def get_queryset(self):
        q_params = Q(user_id=self.request.user.id)

        # get values to filter classes
        selected_location = self.request.GET.get('enroll_location', None)
        selected_course = self.request.GET.get('enroll_course', None)
        only_synced = self.request.GET.get('synced', False)

        if selected_course:
            q_params &= Q(course=selected_course)
        if selected_location:
            q_params &= Q(location=selected_location)
        if only_synced:
            q_params &= Q(status=self.model.STATUS_CHOICES.SYNCED)
        else:
            q_params &= ~Q(status=self.model.STATUS_CHOICES.SYNCED)

        qs = self.model.objects.filter(q_params).order_by('start_time')
        return qs

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        aha_fields = {field.type: field.value for field in
                      self.request.user.aha_fields.all()}

        # filters data
        selected_location = self.request.GET.get('enroll_location', None)
        selected_course = self.request.GET.get('enroll_course', None)
        only_synced = self.request.GET.get('synced', False)

        context['synced'] = only_synced
        context['selected_location'] = selected_location
        context['selected_course'] = selected_course
        context['enroll_locations'] = EnrollWareGroup.get_locations()
        context['enroll_courses'] = EnrollWareGroup.get_courses()

        context['aha_fields'] = aha_fields
        if self.request.GET.get('success', None):
            context['info_message'] = {
                'title': 'Congratulations!',
                'text': "You're about to free up a lot of your time. And be able to market your classes on other sites!"
            }
        else:
            context['info_message'] = {
                'title': 'Teach ClassBlast',
                'text': "ClassBlast found your Enrollware classes. Everyone has their own naming format for their classes which are not the same as AHA’s naming format - we need you to teach ClassBlast how to work. Please map your class info with AHA’s options. Don’t worry, you only have to do  this once for each class."
            }
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


class PaymentView(LoginRequiredMixin, View):
    """
    Stripe default settings View
    """
    login_url = '/auth/login/'
    redirect_field_name = ''
    template_name = 'dashboard.html'

    def post(self, request):
        # Set your secret key: remember to change this to your live secret key in production
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = settings.TEST_STRIPE_API_KEY

        # Token is created using Checkout or Elements!
        # Get the payment token ID submitted by the form:
        token = request.POST['stripeToken']

        # Charge the user's card:
        charge = stripe.Charge.create(
            amount=settings.TEST_STRIPE_AMOUNT,
            currency="usd",
            description="Pro plan charge",
            source=token,
        )
        if charge.paid:
            request.user.version = request.user.VERSIONS.PRO
            request.user.save()

        return redirect(reverse_lazy('dashboard:manage'))


class ImportGroupsFromCSV(LoginRequiredMixin, View):
    template_name = 'dashboard.html'

    def post(self, request):

        DATE_FORMAT = '%m/%d/%y %H:%M'

        file = request.FILES['csv_file']

        if request.FILES:
            logger.info("{} Import from CSV by {}".format("---> ",
                                                           self.request.user.username))
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            for index, row in enumerate(
                    csv.DictReader(io_string, delimiter=',')):
                try:
                    start_time = datetime.strptime(row['Start Date / Time'],
                                                   DATE_FORMAT)

                    end_time = datetime.strptime(row['End Date / Time'],
                                                 DATE_FORMAT)
                    max_students = int(row['Students']) + int(row['Seats'])

                except KeyError as e:
                    logger.info(
                        "Error while processing field: {}".format(str(e)))
                    messages.error(request, 'File contains invalid fields: {}'.format(str(e)))
                    return redirect(reverse_lazy('dashboard:manage'))
                except ValueError as e:
                    msg = "Can not parse value in row {row_number}: " \
                          "for course {course}: {start_time} - {end_time}".format(
                        row_number=index + 1, course=row['Course'],
                        start_time=row['Start Date / Time'],
                        end_time=row['End Date / Time']
                    )
                    logger.info(msg)
                    messages.error(request, msg)
                    return redirect(reverse_lazy('dashboard:manage'))
                """
                available_to_export=True, cause this option available only in a
                PRO-version
                """
                group, created = EnrollWareGroup.objects.get_or_create(
                    user=self.request.user,
                    course=row['Course'],
                    location=row['Location'],
                    instructor=row['Instructor'],
                    max_students=max_students,
                    start_time=start_time,
                    end_time=end_time,
                    defaults={'group_id': uuid.uuid4(),
                              'status': EnrollWareGroup.STATUS_CHOICES.UNSYNCED,
                              'available_to_export': True},
                )
            logger.info("Classes successfully imported from CSV")
            messages.success(request, 'Classes successfully imported')
        return redirect(
            reverse_lazy('dashboard:manage'))
