import time

from apps.core.celery import app
from scraper.aha.exporter import AHAExporter
from apps.core.models import EnrollWareGroup


@app.task
def export_to_aha(username, password, group_data):
    exporter = AHAExporter(username, password, group_data)

    print("task ...")
    ew_group = EnrollWareGroup.objects.filter(
        id=group_data['enroll_id']).first()
    ew_group.status = EnrollWareGroup.STATUS_CHOICES.IN_PROGRESS
    ew_group.save()
    # TODO: handle error, show message
    try:
        print("TRY")
        exporter.run()
    except Exception as e:
        print("not ok")
        ew_group.status = EnrollWareGroup.STATUS_CHOICES.ERROR
    else:
        ew_group.status = EnrollWareGroup.STATUS_CHOICES.SYNCED

    ew_group.save()

    print("ok")
