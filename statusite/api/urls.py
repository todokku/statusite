from django.conf.urls import include
from django.conf.urls import url

from statusite.repository import views as repository_views
from statusite.youtube import views as youtube_views


urlpatterns = [
    url(
        r'repository/(?P<owner>\w+)/(?P<repo>[^/].*)$',
        repository_views.api_repository.as_view(),
        name='api-repository',
    ),
    url(
        r'^youtube/playlists/(?P<youtube_id>\w+)$',
        youtube_views.PlaylistView.as_view(),
        name='api-playlist',
    ),
]
