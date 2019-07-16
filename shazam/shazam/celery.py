from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shazam.settings')

from django.conf import settings

app = Celery('shazam')


app.config_from_object('django.conf:settings')
app.autodiscover_tasks() #Nota 3
 
app.conf.update(
    BROKER_URL = 'amqp://localhost', 
)