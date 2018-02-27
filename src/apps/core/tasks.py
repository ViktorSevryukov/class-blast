import time

from apps.core.celery import app
from scraper.aha.exporter import AHAExporter
from apps.core.models import EnrollWareGroup


@app.task
def export_to_aha(username, password, group_data):
    exporter = AHAExporter(username, password, group_data)

    print("task ...")
    current_id = group_data['enroll_id']
    current_group = EnrollWareGroup.objects.filter(id=current_id).first()
    current_group.status = EnrollWareGroup.STATUS_CHOICES.IN_PROGRESS
    current_group.save()
    # TODO: handle error, show message
    try:
        time.sleep(5)
        print("TRY")
    except Exception as e:
        print("not ok")
        current_group.status = EnrollWareGroup.STATUS_CHOICES.ERROR
        current_group.save()
    else:
        current_group.status = EnrollWareGroup.STATUS_CHOICES.SYNCED
        current_group.save()
        pass
    print("ok")
    return True