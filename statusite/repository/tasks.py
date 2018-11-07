from django import db
import django_rq

from statusite.repository.models import Repository


MAX_BETA = 1  # we only need the latest
MAX_PRODUCTION = 5  # get a few latest in case push dates are canceled


@django_rq.job("default", timeout=60)
def update_latest_releases():
    db.connection.close()
    n = 0

    def reload_releases(releases, beta=False):
        nonlocal n
        for k, release in enumerate(releases.filter(beta=beta), start=1):
            if k > (MAX_BETA if beta else MAX_PRODUCTION):
                break
            release.reload()
            n += 1

    for repo in Repository.objects.all():
        reload_releases(repo.releases)
        reload_releases(repo.releases, beta=True)
    return "Updated {} releases".format(n)
