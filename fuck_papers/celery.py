from __future__ import absolute_import
from celery import Celery


app = Celery('fuck_papers', include=['fuck_papers.tasks'])

app.config_from_object('fuck_papers.celeryconfig')
# app.autodiscover_tasks()


if __name__ == '__main__':
    app.start()
