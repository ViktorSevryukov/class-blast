from apps.auth_core.models import User
from apps.core.celery import app
from apps.core.models import EnrollClassTime, AHACredentials, EnrollWareGroup, AHAField, Mapper
from scraper.aha.exporter import AHAExporter


@app.task
def export_to_aha(exported_groups, user_id):

    user = User.objects.filter(id=user_id).first()

    for group in exported_groups:

        # TODO: add try except, return Error if something not found
        enroll_group = EnrollWareGroup.objects.filter(id=group['enroll_group_id']).first()

        class_time = EnrollClassTime.objects.filter(group_id=enroll_group.group_id).first()

        aha_auth_data = AHACredentials.objects.filter(user=user_id).last()

        group_data = {
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

        # TODO: fix user literal

        MAPPER_FIELDS = (AHAField.FIELD_TYPES.COURSE, AHAField.FIELD_TYPES.LOCATION, AHAField.FIELD_TYPES.INSTRUCTOR)

        # TODO: parallel function
        for field in MAPPER_FIELDS:
            Mapper.objects.update_or_create(
                aha_field=AHAField.objects.filter(type=field).first(),
                enroll_value=getattr(enroll_group, field),
                user=user,
                defaults={'aha_value': group['aha_data'][field]}
            )

        exporter = AHAExporter(aha_auth_data.username, aha_auth_data.password, group_data)

        # TODO: handle error, show message
        try:
            exporter.run()
        except Exception as e:
            return False

        return True
