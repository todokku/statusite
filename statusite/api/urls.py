from django.conf.urls import include
from django.conf.urls import url

from statusite.youtube import views as youtube_views


urlpatterns = [
    url(
        r'^youtube/playlists/(?P<youtube_id>\w+)$',
        youtube_views.PlaylistView.as_view(),
        name='playlist',
    ),
]
