import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from statusite.youtube.models import Playlist


class PlaylistView(View):

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        return super(PlaylistView, self).dispatch(*args, **kwargs)

    def get(self, request, youtube_id):
        playlist = get_object_or_404(Playlist, youtube_id=youtube_id)
        return JsonResponse(json.loads(playlist.json_str))
