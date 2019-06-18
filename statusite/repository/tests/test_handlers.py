from datetime import datetime

import pytest
import responses

from statusite.repository.handlers import set_github_id


class TestHandlers:
    @pytest.mark.django_db
    @responses.activate
    def test_set_github_id(self, repository_factory, mock_github_repo_response):
        repo = repository_factory(github_id=None)
        repo.refresh_from_db()
        assert repo.github_id == 1234567890
