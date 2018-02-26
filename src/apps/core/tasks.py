from apps.core.celery import app
from scraper.aha.exporter import AHAExporter


@app.task
def export_to_aha(username, password, group_data):
    exporter = AHAExporter(username, password, group_data)

    print("task ...")
    # TODO: handle error, show message
    try:
        pass
        # exporter.run()
    except Exception as e:
        print("not ok")
        return False
    print("ok")
    return True