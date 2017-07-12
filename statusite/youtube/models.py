from datetime import date
from datetime import datetime
import json

from django.db import models

from statusite.youtube.utils import youtube_api_wrapper


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError('Type {} not serializable'.format(type(obj)))


class Playlist(models.Model):
    youtube_id = models.CharField(max_length=255)
    json_str = models.TextField(blank=True, editable=False, null=True)
    title = models.CharField(
        blank=True,
        editable=False,
        max_length=255,
        null=True,
    )

    def __str__(self):
        return self.title if self.title else self.youtube_id

    def reload(self):
        youtube_api = youtube_api_wrapper()
        results = youtube_api.playlists().list(
            id=self.youtube_id,
            part='snippet',
        ).execute()
        self.json_str = json.dumps(results['items'][0], default=json_serial)
        self.title = results['items'][0]['snippet']['title']
        self.save()
