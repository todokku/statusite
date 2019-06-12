from __future__ import unicode_literals

from django.apps import AppConfig


class YoutubeConfig(AppConfig):
    name = "statusite.youtube"

    def ready(self):
        # side-effect import to register handler
        import statusite.youtube.handlers  # noqa
