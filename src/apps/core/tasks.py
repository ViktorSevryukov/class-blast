from apps.auth_core.models import User
from apps.core.celery import app
from apps.core.models import EnrollWareGroup, EnrollWareCredentials, \
    AHACredentials

from scraper.aha.exporter import AHAExporter
from scraper.aha.importer import AHAImporter
from scraper.enrollware.importer import ClassImporter

import logging

aha_export_logger = logging.getLogger('aha_export')
aha_import_logger = logging.getLogger('aha_import')
enroll_logger = logging.getLogger('enroll')


@app.task
def export_to_aha(username, password, group_data):
    exporter = AHAExporter(username, password, group_data, logger_name='aha_export')

    aha_export_logger.info("AHA export task ...")
    ew_group = EnrollWareGroup.objects.filter(
        id=group_data['enroll_id']).first()
    ew_group.status = EnrollWareGroup.STATUS_CHOICES.IN_PROGRESS
    ew_group.save()
    try:
        exporter.run()
    except Exception as msg:
        aha_export_logger.info("error: {}".format(msg))
        ew_group.status = EnrollWareGroup.STATUS_CHOICES.ERROR
        ew_group.save()
        raise Exception(msg)
    else:
        aha_export_logger.info("export ended")
        ew_group.status = EnrollWareGroup.STATUS_CHOICES.SYNCED
        ew_group.save()
        # ew_group.available_to_export = False


@app.task
def import_enroll_groups(username, password, user_id):
    user = User.objects.get(id=user_id)
    importer = ClassImporter(username, password, user)
    enroll_logger.info("Enroll import start")

    try:
        importer.run()
    except Exception as msg:
        enroll_logger.info("error: {}".format(msg))
        raise Exception(msg)
    else:
        user.set_available_to_export_groups()

        enroll_logger.info("import success")

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
    importer = AHAImporter(username, password, user, logger_name='aha_importer')
    aha_import_logger.info("AHA import start")
    try:
        importer.run()
    except Exception as msg:
        aha_import_logger.info("error: {}".format(msg))
        raise Exception(msg)

    aha_import_logger.info("import success")

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
