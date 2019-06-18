import re

from django.utils.dateparse import parse_datetime


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
        r"(?P<type>sandbox|production) orgs: (?P<date>\d\d\d\d-\d\d-\d\d)",
        re.IGNORECASE,
    )
    for line in release_notes.splitlines():
        m = reobj.match(line)
        if m:
            if m.group("type") == "Sandbox":
                time_sandbox = parse_time(m.group("date"))
            else:
                time_production = parse_time(m.group("date"))
    return time_sandbox, time_production
