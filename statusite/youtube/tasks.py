from django import db
import django_rq

from statusite.youtube.models import Playlist


@django_rq.job("default", timeout=600)
def update_playlists():
    db.connection.close()
    n = 0
    for playlist in Playlist.objects.all():
        update_playlist.delay(playlist.id)
        n += 1
    return "Queued {} playlists for update".format(n)


@django_rq.job("default", timeout=600)
def update_playlist(playlist_id):
    db.connection.close()
    playlist = Playlist.objects.get(id=playlist_id)
    playlist.reload()
    return "Updated playlist {}".format(playlist_id)
