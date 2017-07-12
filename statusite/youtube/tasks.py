from django import db
import django_rq

from statusite.youtube.models import Playlist


@django_rq.job('default', timeout=600)
def update_playlists():
    db.connection.close()
    n = 0
    for playlist in Playlist.objects.all():
        playlist.reload()
        n += 1
    return 'Updated {} playlists'.format(n)
