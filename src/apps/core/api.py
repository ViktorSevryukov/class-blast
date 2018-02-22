from django.shortcuts import redirect
from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework.reverse import reverse_lazy

from apps.core.models import EnrollClassTime, AHACredentials, EnrollWareGroup, AHAField, Mapper
from scraper.aha.exporter import AHAExporter


@api_view(['POST'])
def export_group(request):
    print(request.data)
    return Response({"OLOLO":"OLOLO"})
    exported_groups = request.POST.get('exportedGroups', None)


    for group in exported_groups:

        class_time = EnrollClassTime.objects.filter(
            group_id=group['enroll_group_id']).first()

        aha_auth_data = AHACredentials.objects.filter(user=request.user).last()
        enroll_group = EnrollWareGroup.objects.filter(group_id=request.POST['enroll_group_id']).first()

        group_data = {
            'course': group['aha_data']['course'],
            'language': "English",
            'location': group['aha_data']['location'] + " ",
            'tc': group['aha_data']['training_center'],
            'ts': group['aha_data']['training_site'],
            'instructor': group['aha_data']['instructor'],
            'date': class_time.date,
            'from': class_time.start,
            'to': class_time.end,
            'class_description': group['aha_data']['class_description'],
            'roster_limit': group['aha_data']['roster_limit'],
            'cutoff_date': group['aha_data']['cutoff_date'],
            'class_notes': group['aha_data']['class_notes']
        }

        # TODO: fix user literal

        MAPPER_FIELDS = (AHAField.FIELD_TYPES.COURSE, AHAField.FIELD_TYPES.LOCATION, AHAField.FIELD_TYPES.INSTRUCTOR)

        # TODO: parallel function
        for field in MAPPER_FIELDS:
            Mapper.objects.update_or_create(
                aha_field=AHAField.objects.filter(type=field).first(),
                enroll_value=getattr(enroll_group, field),
                user=request.user,
                defaults={'aha_value': request.POST[field]}
            )

        exporter = AHAExporter(aha_auth_data.username, aha_auth_data.password, group_data)

        # TODO: handle error, show message
        try:
            exporter.run()
        except:
            return redirect(reverse_lazy('dashboard:manage'))

