from apps.auth_core.models import User
from apps.core.celery import app
from apps.core.models import EnrollWareGroup, EnrollWareCredentials, \
    AHACredentials

from scraper.aha.exporter import AHAExporter
from scraper.aha.importer import AHAImporter
from scraper.enrollware.importer import ClassImporter


@app.task
def export_to_aha(username, password, group_data):
    exporter = AHAExporter(username, password, group_data)

    print("task ...")
    ew_group = EnrollWareGroup.objects.filter(
        id=group_data['enroll_id']).first()
    ew_group.status = EnrollWareGroup.STATUS_CHOICES.IN_PROGRESS
    ew_group.save()
    # TODO: handle error, show message
    print("TRY")
    success, message = exporter.run()
    if not success:
        print("not ok - {}".format(message))
        ew_group.status = EnrollWareGroup.STATUS_CHOICES.ERROR
        ew_group.save()
        export_to_aha.update_state(state='FAILURE', meta={'exc': message})
    else:
        print("ok")
        ew_group.status = EnrollWareGroup.STATUS_CHOICES.SYNCED
        # ew_group.available_to_export = False
    ew_group.save()


@app.task
def import_enroll_groups(username, password, user_id):
    user = User.objects.get(id=user_id)
    importer = ClassImporter(username, password, user)
    success, message = importer.run()
    if not success:
        print("not ok - {}".format(message))
        return False, message
    else:
        user.set_available_to_export_groups()

        return {
            'username': username,
            'password': password,
            'user_id': user_id
        }


@app.task
def update_enroll_credentials(result):
    user = User.objects.get(id=result['user_id'])

    EnrollWareCredentials.objects.update_or_create(
        username=result['username'],
        user=user,
        defaults={'password': result['password']}
    )


# TODO: user auth model
@app.task
def import_aha_fields(username, password, user_id):
    user = User.objects.get(id=user_id)
    importer = AHAImporter(username, password, user)
    importer.run()
    return {
        'username': username,
        'password': password,
        'user_id': user_id
    }


# TODO: use content type
@app.task
def update_aha_credentials(result):
    user = User.objects.get(id=result['user_id'])

    AHACredentials.objects.update_or_create(
        username=result['username'],
        user=user,
        defaults={'password': result['password']}
    )
