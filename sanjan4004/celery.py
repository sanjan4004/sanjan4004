import os
from celery import Celery
import redis


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sanjan4004.settings")  # Change "project_root" to your actual project name

app = Celery("WorldTtance")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()




# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjan4004.settings')

app = Celery('sanjan4004')

# Load Celery config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()


