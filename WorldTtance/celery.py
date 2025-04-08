import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sanjan4004.settings")

app = Celery("WorldTtance")

# Load Celery settings from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in installed Django apps
app.autodiscover_tasks()
