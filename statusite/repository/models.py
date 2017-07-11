from __future__ import unicode_literals

from django.db import models
from django.urls import reverse

from github3 import login
from django.conf import settings

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

    def __unicode__(self):
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

    class Meta:
        ordering = ['repo__product_name', '-time_created']
        
    def get_absolute_url(self):
        return reverse('release_detail', kwargs={'owner': self.owner, 'name': self.name})

    def reload(self):
        github = self.repo.github_api
        release = github.release(self.github_id)
        body = release.body
        if not body:
            body = ''
        self.release_notes = body
        self.save()

    @property
    def release_notes_html(self):
        if not self.release_notes:
            return None
        github = self.repo.github_api_root
        html = github.markdown(self.release_notes, mode='gfm', context='{}/{}'.format(self.repo.owner, self.repo.name))
        return html

    def __unicode__(self):
        return '{}: {}'.format(self.repo.product_name, self.version)
