import os
import sys

from celery import Celery
from django.conf import settings

sys.path.append('..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery('core', broker='amqp://guest:guest@localhost:5672//', backend='amqp://')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
