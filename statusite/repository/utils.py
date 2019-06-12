import re

from django.conf import settings
from django.utils.dateparse import parse_datetime
from github3 import login


def create_status(build):
    if not build.plan.context:
        # skip setting Github status if the context field is empty
        return

    github = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
    repo = github.repository(build.repo.owner, build.repo.name)

    if build.status == "queued":
        state = "pending"
        description = "The build is queued"
    if build.status == "waiting":
        state = "pending"
        description = "The build is waiting for another build to complete"
    if build.status == "running":
        state = "pending"
        description = "The build is running"
    if build.status == "success":
        state = "success"
        description = "The build was successful"
    elif build.status == "error":
        state = "error"
        description = "An error occurred during build"
    elif build.status == "fail":
        state = "failure"
        description = "Tests failed"

    response = repo.create_status(
        sha=build.commit,
        state=state,
        target_url=build.get_external_url(),
        description=description,
        context=build.plan.context,
    )

    return response


def parse_times(release_notes):
    """ Parse push times from release notes text """

    def parse_time(date):
        """Convert date string into timezone-aware object
        Assume time is 00:00 UTC for the parsed date.
        """
        return parse_datetime(date + " 00:00+00")

    time_sandbox = None
    time_production = None
    if not release_notes:
        return time_sandbox, time_production
    reobj = re.compile(
        r"(?P<type>sandbox|production) orgs: (?P<date>\d\d\d\d-\d\d-\d\d)", re.IGNORECASE
    )
    for line in release_notes.splitlines():
        m = reobj.match(line)
        if m:
            if m.group("type") == "Sandbox":
                time_sandbox = parse_time(m.group("date"))
            else:
                time_production = parse_time(m.group("date"))
    return time_sandbox, time_production
