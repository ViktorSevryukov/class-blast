import stripe
from django.conf import settings
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

        return render(request, self.template_name, context)


class DashboardView(LoginRequiredMixin, ListView):
    model = EnrollWareGroup
    template_name = 'dashboard.html'
    context_object_name = 'ew_groups'
    paginate_by = 10
    login_url = '/auth/login/'
    redirect_field_name = ''

    def get_queryset(self):
        qs = self.model.objects.filter(user_id=self.request.user.id).order_by('-modified')
        return qs

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        aha_fields = {field.type: field.value for field in
                      self.request.user.aha_fields.all()}
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
