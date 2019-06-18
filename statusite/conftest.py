from datetime import datetime

import django
import factory
import pytest
import pytz
import responses
from django_rq import get_worker, get_queue
from pytest_factoryboy import register
from rq import Queue
from rq.worker import SimpleWorker

from .repository.models import Repository, Release
from .youtube.models import Playlist


@register
class RepositoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Repository

    name = "TestRepo"
    owner = "TestOwner"
    product_name = "Test"
    github_id = 1
    url = "https://github.com/TestOwner/TestRepo"


@register
class ReleaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Release

    repo = factory.SubFactory(RepositoryFactory)
    name = "1.0"
    version = "1.0"
    github_id = 1
    time_created = datetime(2019, 6, 17, tzinfo=pytz.UTC)


@register
class PlaylistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Playlist

    youtube_id = "some-playlist"
    json_str = "{}"


@pytest.fixture
def mock_github_repo_response():
    owner = "TestOwner"
    name = "TestRepo"
    html_url = "https://github.com/{}/{}".format(owner, name)
    url = "https://api.github.com/repos/{}/{}".format(owner, name)
    owner_url = "https://api.github.com/users/{}".format(owner)
    now = datetime.now().isoformat()
    response_body = {
        "id": 1234567890,
        "name": name,
        "description": "",
        "archived": False,
        "created_at": now,
        "default_branch": "master",
        "fork": False,
        "forks_count": 1,
        "full_name": "{}/{}".format(owner, name),
        "git_url": "git://github.com/{}/{}.git".format(owner, name),
        "has_downloads": False,
        "has_issues": False,
        "has_pages": False,
        "has_projects": False,
        "has_wiki": False,
        "homepage": "",
        "language": "Python",
        "mirror_url": None,
        "network_count": 0,
        "open_issues_count": 0,
        "owner": {
            "id": 1234567891,
            "login": owner,
            "url": owner_url,
            "type": "Organization",
            "site_admin": False,
            "avatar_url": "https://avatars2.githubusercontent.com/u/42554011?v=4",
            "gravatar_id": "",
            "html_url": "https://github.com/{}".format(owner),
            "followers_url": owner_url + "/followers",
            "following_url": owner_url + "/following{/other_user}",
            "gists_url": owner_url + "/gists{/gist_id}",
            "starred_url": owner_url + "/starred{/owner}{/repo}",
            "subscriptions_url": owner_url + "/subscriptions",
            "organizations_url": owner_url + "/orgs",
            "repos_url": owner_url + "/repos",
            "events_url": owner_url + "/events{/privacy}",
            "received_events_url": owner_url + "/received_events",
        },
        "pushed_at": now,
        "private": False,
        "size": 1,
        "ssh_url": "git@github.com:{}/{}.git".format(owner, name),
        "stargazers_count": 0,
        "subscribers_count": 0,
        "svn_url": html_url,
        "updated_at": now,
        "watchers_count": 0,
        "archive_url": url + "/{archive_format}{/ref}",
        "assignees_url": url + "/assignees{/user}",
        "blobs_url": url + "/git/blobs{/sha}",
        "branches_url": url + "/branches{/branch}",
        "clone_url": html_url + ".git",
        "collaborators_url": url + "/collaborators{/collaborator}",
        "comments_url": url + "/comments{/number}",
        "commits_url": url + "/commits{/sha}",
        "compare_url": url + "/compare/{base}...{head}",
        "contents_url": url + "/contents/{+path}",
        "contributors_url": url + "/CumulusCI/contributors",
        "deployments_url": url + "/CumulusCI/deployments",
        "downloads_url": url + "/downloads",
        "events_url": url + "/events",
        "forks_url": url + "/forks",
        "git_commits_url": url + "/git/commits{/sha}",
        "git_refs_url": url + "/git/refs{/sha}",
        "git_tags_url": url + "/git/tags{/sha}",
        "hooks_url": url + "/hooks",
        "html_url": html_url,
        "issue_comment_url": url + "/issues/comments{/number}",
        "issue_events_url": url + "/issues/events{/number}",
        "issues_url": url + "/issues{/number}",
        "keys_url": url + "/keys{/key_id}",
        "labels_url": url + "/labels{/name}",
        "languages_url": url + "/languages",
        "merges_url": url + "/merges",
        "milestones_url": url + "/milestones{/number}",
        "notifications_url": url + "/notifications{?since,all,participating}",
        "pulls_url": url + "/pulls{/number}",
        "releases_url": url + "/releases{/id}",
        "stargazers_url": url + "/stargazers",
        "statuses_url": url + "/statuses/{sha}",
        "subscribers_url": url + "/subscribers",
        "subscription_url": url + "/subscription",
        "tags_url": url + "/tags",
        "teams_url": url + "/teams",
        "trees_url": url + "/git/trees{/sha}",
        "url": url,
    }
    responses.add("GET", url, json=response_body)


@pytest.fixture
def mock_github_release_response():
    now = datetime.now().isoformat()
    url = "https://api.github.com/repos/TestOwner/TestRepo/releases/1"
    release = {
        "url": url,
        "assets": [],
        "assets_url": "",
        "author": _github_user("testuser"),
        "body": "",
        "created_at": now,
        "draft": False,
        "html_url": "",
        "id": 1,
        "name": "release",
        "prerelease": False,
        "published_at": now,
        "tag_name": "",
        "tarball_url": "",
        "target_commitish": "",
        "upload_url": "",
        "zipball_url": "",
    }
    responses.add("GET", url, json=release)


def _github_user(name):
    user_url = "https://api.github.com/users/{}".format(name)
    user = {
        "id": 1234567892,
        "login": name,
        "url": user_url,
        "type": "User",
        "site_admin": False,
        "avatar_url": "https://avatars2.githubusercontent.com/u/42554011?v=4",
        "gravatar_id": "",
        "html_url": "https://github.com/{}".format(name),
        "followers_url": user_url + "/followers",
        "following_url": user_url + "/following{/other_user}",
        "gists_url": user_url + "/gists{/gist_id}",
        "starred_url": user_url + "/starred{/owner}{/repo}",
        "subscriptions_url": user_url + "/subscriptions",
        "organizations_url": user_url + "/orgs",
        "repos_url": user_url + "/repos",
        "events_url": user_url + "/events{/privacy}",
        "received_events_url": user_url + "/received_events",
    }
    return user


@pytest.fixture
def mock_github_markdown_response():
    # pass through input
    responses.add_callback(
        "POST",
        "https://api.github.com/markdown",
        callback=lambda request: (200, {}, request.body),
    )


@pytest.fixture
def worker():
    # Run jobs in the same thread for tests,
    # since Django has problems with the db connection when forking
    get_queue().empty()
    return get_worker(worker_class=SimpleWorker)
