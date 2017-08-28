from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.utils import timezone

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
        ordering = ['name','owner']

    def get_absolute_url(self):
        return reverse('repo_detail', kwargs={'owner': self.owner, 'name': self.name})

    def __str__(self):
        return '{}/{}'.format(self.owner, self.name)
   
    @property 
    def github_api(self):
        gh = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
        gh = gh.repository(self.owner, self.name)
        return gh

    @property 
    def github_api_root(self):
        gh = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
        return gh

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
            if release.time_push_sandbox and release.time_push_sandbox <= timezone.now():
                return release

class Release(models.Model):
    repo = models.ForeignKey(Repository, related_name='releases')
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=32)
    beta = models.BooleanField(default=False)
    release_notes = models.TextField()
    url = models.URLField()
    github_id = models.IntegerField()
    time_created = models.DateTimeField()
    time_push_sandbox = models.DateTimeField(null=True, blank=True)
    time_push_prod = models.DateTimeField(null=True, blank=True)
    tag = models.CharField(max_length=255)

    class Meta:
        ordering = ['repo__product_name', '-time_created']
        
    def get_absolute_url(self):
        return reverse('release_detail', kwargs={'owner': self.owner, 'name': self.name})

    def reload(self):
        github = self.repo.github_api
        release = github.release(self.github_id)
        if release:
            self.release_notes = release.body
            self.time_push_sandbox, self.time_push_prod = parse_times(
                release.body)
            self.save()
        else:
            raise RepoReloadError(
                '\nGitHub repo: {}\n'.format(github.html_url) +
                'GitHub release ID: {}\n'.format(self.github_id) +
                'release: {}'.format(release)
            )

    @property
    def release_notes_html(self):
        if not self.release_notes:
            return None
        github = self.repo.github_api_root
        html = github.markdown(self.release_notes, mode='gfm', context='{}/{}'.format(self.repo.owner, self.repo.name))
        return html

    def __str__(self):
        return '{}: {}'.format(self.repo.product_name, self.version)


class BuildResult(models.Model):
    class Meta:
        verbose_name = 'Build Result'

    repo = models.ForeignKey(Repository, related_name='build_results')
    release = models.ForeignKey(Release, related_name='build_results')
    plan_name = models.CharField(max_length=255)
    mbci_build_id = models.IntegerField('mrbelvedereci build id')
    status = models.CharField(max_length=25)
    build_date = models.DateField()
    tests_passed = models.IntegerField()
    tests_failed = models.IntegerField()
    tests_total = models.IntegerField()
    # TODO: additional build stats

    def __str__(self):
        return '{}: {} [Build {}]'.format(self.repo.product_name, self.release.version, self.mbci_build_id)