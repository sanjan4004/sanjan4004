from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from WorldTtance.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Only create profile if the user is new
        UserProfile.objects.create(user=instance)
