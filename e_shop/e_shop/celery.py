import os
from celery import Celery

# Укажите название вашего Django-проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_shop.settings")

app = Celery("e_shop")
# Загрузка конфигурации Celery из settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()