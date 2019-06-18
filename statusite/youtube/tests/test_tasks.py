from django import db
import pytest

from statusite.youtube.tasks import update_playlists


class TestTasks:
    @pytest.mark.django_db
    def test_update_playlists(self, playlist_factory, worker, mocker):
        mock_reload = mocker.patch("statusite.youtube.models.Playlist.reload")
        playlist = playlist_factory()

        update_playlists.delay()
        worker.work(burst=True)

        # Queued once from playlist's post_save handler,
        # and once from update_playlists
        assert mock_reload.call_count == 2
