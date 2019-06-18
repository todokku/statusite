import pytest


class TestPlaylistView:
    @pytest.mark.django_db
    def test_get(self, client, playlist_factory):
        playlist = playlist_factory()

        response = client.get("/api/youtube/playlists/some-playlist")

        assert response.status_code == 200
        assert response.json() == {}
