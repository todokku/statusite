from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.utils import timezone
from model_utils.models import SoftDeletableModel
from github3 import login
from django.conf import settings

from statusite.repository.exceptions import RepoReloadError
from statusite.repository.utils import parse_times


class Repository(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    github_id = models.IntegerField(null=True, blank=True)
    url = models.URLField(max_length=255)

    class Meta:
        ordering = ["name", "owner"]
        verbose_name_plural = "repositories"

    def get_absolute_url(self):
        return reverse(
            "repository:repository-detail", kwargs={"owner": self.owner, "name": self.name}
        )

    def __str__(self):
        return "{}/{}".format(self.owner, self.name)

    @property
    def latest_release(self):
        release = self.releases.filter(beta=False)[:1]
        if release:
            return release[0]

    @property
    def latest_beta(self):
        release = self.releases.filter(beta=True)[:1]
        if release:
            return release[0]

    @property
    def production_release(self):
        for release in self.releases.filter(beta=False):
            if release.time_push_prod and release.time_push_prod <= timezone.now():
                return release

    @property
    def sandbox_release(self):
        for release in self.releases.filter(beta=False):
            if (
                release.time_push_sandbox
                and release.time_push_sandbox <= timezone.now()
            ):
                return release


class Release(SoftDeletableModel):
    repo = models.ForeignKey(Repository, related_name="releases", on_delete=models.deletion.CASCADE)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=32)
    beta = models.BooleanField(default=False)
    release_notes = models.TextField()
    release_notes_html = models.TextField()
    url = models.URLField()
    github_id = models.IntegerField()
    time_created = models.DateTimeField()
    time_push_sandbox = models.DateTimeField(null=True, blank=True)
    time_push_prod = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["repo__product_name", "-time_created"]

    def get_absolute_url(self):
        return reverse(
            "release-detail", kwargs={"owner": self.owner, "name": self.name}
        )

    def reload(self):
        api_gh = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
        api_repo = api_gh.repository(self.repo.owner, self.repo.name)
        release = api_repo.release(self.github_id)
        if release:
            release_notes = release.body if release.body else ""
            self.release_notes = release_notes
            self.release_notes_html = api_gh.markdown(
                release_notes,
                mode="gfm",
                context="{}/{}".format(self.repo.owner, self.repo.name),
            )
            self.time_push_sandbox, self.time_push_prod = parse_times(release_notes)
            self.save()
        else:
            self.delete()

    def __str__(self):
        return "{}: {}".format(self.repo.product_name, self.version)
