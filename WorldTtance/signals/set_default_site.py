# myapp/signals.py

from django.db.models.signals import post_migrate
from django.contrib.sites.models import Site
from django.conf import settings

def set_default_site(sender, **kwargs):
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            "domain": "worldttance.com",
            "name": "WorldTtance"
        },
    )

post_migrate.connect(set_default_site)
