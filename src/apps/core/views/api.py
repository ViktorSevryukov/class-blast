import json
import csv

from celery import chain
from celery.result import AsyncResult
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

from rest_framework import status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import EnrollWareGroup, EnrollClassTime, AHACredentials, \
    AHAField, Mapper
from apps.core.tasks import export_to_aha, import_enroll_groups, \
    update_enroll_credentials, import_aha_fields, update_aha_credentials, User


class ImportEnroll(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):

        try:
            credentials = json.loads(request.data['credentials'])
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        username = credentials.get('login', None)
        password = credentials.get('password', None)

        if not (username and password):
            credentials = request.user.enrollwarecredentials.first()

            if credentials:
                username = credentials.username
                password = credentials.password

            if not (credentials and username and password):
                return Response({'details': _("Credentials not valid")},
                                status=status.HTTP_400_BAD_REQUEST)
        res = chain(
            import_enroll_groups.s(username, password,
                                   request.user.id),
            update_enroll_credentials.s()
        )()

        return Response(
            {'details': _("Task in progress"), 'tasks': [res.parent.id]})


class ImportAHA(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):

        try:
            credentials = json.loads(request.data['credentials'])
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        username = credentials.get('login', None)
        password = credentials.get('password', None)

        if not (username and password):
            credentials = request.user.ahacredentials.first()

            if credentials:
                username = credentials.username
                password = credentials.password

            if not (credentials and username and password):
                return Response({'details': _("Credentials not valid")},
                                status=status.HTTP_400_BAD_REQUEST)
        res = chain(
            import_aha_fields.s(username, password, request.user.id),
            update_aha_credentials.s()
        )()

        return Response(
            {'details': _("Task in progress"), 'tasks': [res.parent.id]})


@api_view(['POST'])
def export_group(request):
    try:
        groups = json.loads(request.data['groups'])
    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    tasks = []
    user = request.user

    for group in groups:

        try:
            enroll_group = EnrollWareGroup.objects.filter(
                id=group['enroll_group_id'], available_to_export=True).first()
        except:
            return Response({'details': _("Invalid group id")},
                            status=status.HTTP_400_BAD_REQUEST)

        class_time = EnrollClassTime.objects.filter(
            group_id=enroll_group.group_id).first()

        # TODO: use lookups
        aha_auth_data = AHACredentials.objects.filter(user=user).last()

        # TODO: validate selects (can not be empty)
        group_data = {
            'enroll_id': enroll_group.id,
            'course': group['aha_data']['course'],
            'language': "English",
            'location': group['aha_data']['location'] + " ",
            'tc': group['aha_data']['tc'],
            'ts': group['aha_data']['ts'],
            'instructor': group['aha_data']['instructor'],
            'date': class_time.date,
            'from': class_time.start,
            'to': class_time.end,
            'class_description': group['aha_data']['class_description'],
            'roster_limit': group['aha_data']['roster_limit'],
            'cutoff_date': group['aha_data']['cutoff_date'],
            'class_notes': group['aha_data']['class_notes']
        }

        MAPPER_FIELDS = (
            AHAField.FIELD_TYPES.COURSE, AHAField.FIELD_TYPES.LOCATION,
            AHAField.FIELD_TYPES.INSTRUCTOR, AHAField.FIELD_TYPES.CLASS_DESCRIPTION,
            AHAField.FIELD_TYPES.CLASS_NOTES)

        for field in MAPPER_FIELDS:
            Mapper.objects.update_or_create(
                aha_field=AHAField.objects.filter(type=field).first(),
                enroll_value=getattr(enroll_group, field, enroll_group.course),
                user=user,
                defaults={'aha_value': group['aha_data'][field]}
            )

        task = export_to_aha.delay(aha_auth_data.username,
                                   aha_auth_data.password, group_data)
        tasks.append(task.id)

    return Response({'details': _("Tasks in progress"), 'tasks': tasks},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def check_tasks(request):
    try:
        tasks = json.loads(request.data['tasks'])

    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    failed_tasks, success_tasks, ready_tasks = [], [], []

    for task in tasks:

        task_result = AsyncResult(task)

        if task_result.failed():
            failed_tasks.append({
                'task': task,
                'message': task_result.info.args[0]
            })

        if task_result.successful():
            success_tasks.append(task)

        if task_result.ready():
            ready_tasks.append(task)

    if len(tasks) == len(success_tasks):
        return Response({'code': 'SUCCESS'})  # all task success

    if len(tasks) != len(ready_tasks):
        return Response({'code': 'WAIT'})

    return Response({'code': 'FAILED', 'tasks': failed_tasks})
