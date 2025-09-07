from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Video
from .api.tasks import process_video

@receiver(post_save, sender=Video)
def trigger_processing(sender, instance, created, **kwargs):
    """Trigger video processing after Video creation."""
    
    if created:
        transaction.on_commit(lambda: process_video.delay(instance.id))
