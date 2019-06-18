import pytest

from statusite.repository.tasks import update_latest_releases


class TestTasks:
    @pytest.mark.django_db
    def test_update_latest_releases(self, release_factory, worker, mocker):
        mocker.patch("statusite.repository.models.Release.reload")
        release1 = release_factory(beta=True)
        release2 = release_factory(repo=release1.repo, beta=True)

        job = update_latest_releases.delay()
        worker.work(burst=True)
        assert job.result == "Updated 1 releases"
