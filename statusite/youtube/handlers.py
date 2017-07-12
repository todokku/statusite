from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq

from statusite.youtube.models import Playlist


@receiver(post_save, sender=Playlist)
def init_playlist_data(sender, **kwargs):
    if kwargs['created']:
        queue = django_rq.get_queue('default')
        queue.enqueue_call(
            func=kwargs['instance'].reload,
            timeout=600,
        )
