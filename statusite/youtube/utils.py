from apiclient.discovery import build
from django.conf import settings


class YoutubeApiWrapper(object):
    def __call__(self):
        if not hasattr(self, "youtube_api"):
            self.set_api()
        return self.youtube_api

    def set_api(self):
        self.youtube_api = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)


youtube_api_wrapper = YoutubeApiWrapper()
