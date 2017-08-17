import re

from django.conf import settings
from django.utils.dateparse import parse_datetime
from github3 import login
import pytz


def create_status(build):
    if not build.plan.context:
        # skip setting Github status if the context field is empty
        return

    github = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
    repo = github.repository(build.repo.owner, build.repo.name)

    if build.status == 'queued':
        state = 'pending'
        description = 'The build is queued'
    if build.status == 'waiting':
        state = 'pending'
        description = 'The build is waiting for another build to complete'
    if build.status == 'running':
        state = 'pending'
        description = 'The build is running'
    if build.status == 'success':
        state = 'success'
        description = 'The build was successful'
    elif build.status == 'error':
        state = 'error'
        description = 'An error occurred during build'
    elif build.status == 'fail':
        state = 'failure'
        description = 'Tests failed'

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
    def get_tz_time(s):
        """Convert date string into timezone-aware object
        Assume time is 6:00 PM and timezone is US Pacific
        (This is when we schedule push upgrades to begin)
        """
        s += ' 18:00:00'
        naive = parse_datetime(s)
        return pytz.timezone('US/Pacific').localize(naive,
            is_dst=True)
    time_sandbox = None
    time_production = None
    reobj = re.compile(
        '(?P<type>Sandbox|Production) orgs: (?P<date>\d\d\d\d-\d\d-\d\d)')
    for line in release_notes.splitlines():
        m = reobj.match(line)
        if m:
            if m.group('type') == 'Sandbox':
                time_sandbox = get_tz_time(m.group('date'))
            else:
                time_production = get_tz_time(m.group('date'))
    return time_sandbox, time_production
