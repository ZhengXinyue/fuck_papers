from __future__ import absolute_import
from celery import Celery


app = Celery('parse_paper_and_notify', include=['fuck_papers.spider'])

app.config_from_object('fuck_papers.celeryconfig')
