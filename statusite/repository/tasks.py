from django import db
import django_rq

from statusite.repository.models import Repository


@django_rq.job('default', timeout=60)
def update_latest_releases():
    db.connection.close()
    n = 0
    for repo in Repository.objects.all():
        release = repo.latest_release
        if release:
            release.reload()
            n += 1
        release_beta = repo.latest_beta
        if release_beta:
            release_beta.reload()
            n += 1
    return 'Updated {} releases'.format(n)