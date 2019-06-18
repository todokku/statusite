import responses
import pytest

from statusite.repository.models import Repository


class TestRepository:
    def test_get_absolute_url(self):
        repo = Repository(owner="TestOwner", name="TestRepo")
        assert repo.get_absolute_url() == "/api/repository/TestOwner/TestRepo"

    def test_str(self):
        repo = Repository(owner="TestOwner", name="TestRepo")
        assert str(repo) == "TestOwner/TestRepo"


class TestRelease:
    @pytest.mark.django_db
    def test_get_absolute_url(self, release_factory):
        release = release_factory()
        assert release.get_absolute_url() == "/api/repository/TestOwner/TestRepo/1.0"

    @pytest.mark.django_db
    def test_str(self, release_factory):
        release = release_factory()
        assert str(release) == "Test: 1.0"

    @pytest.mark.django_db
    @responses.activate
    def test_reload(
        self,
        release_factory,
        mock_github_repo_response,
        mock_github_release_response,
        mock_github_markdown_response,
    ):
        release = release_factory()
        release.reload()

    @pytest.mark.django_db
    @responses.activate
    def test_reload_not_found(
        self, release_factory, mock_github_repo_response, mock_github_markdown_response
    ):
        responses.add(
            "GET",
            "https://api.github.com/repos/TestOwner/TestRepo/releases/1",
            status=404,
        )

        release = release_factory()
        release.reload()
