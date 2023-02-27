import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
app = Celery("shop")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'get_products_statistic': {
        'task': 'api.tasks.get_products_statistic',
        'schedule': 10.0,
        # 'schedule': crontab(),
    },
    'get_category_statistic': {
        'task': 'api.tasks.get_category_statistic',
        'schedule': crontab(),
    },
}
