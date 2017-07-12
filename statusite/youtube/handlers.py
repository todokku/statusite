from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq

from statusite.youtube.models import Playlist
from statusite.youtube.tasks import update_playlist


@receiver(post_save, sender=Playlist)
def init_playlist_data(sender, **kwargs):
    if kwargs['created']:
        update_playlist.delay(kwargs['instance'].id)
