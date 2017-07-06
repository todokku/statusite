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
        repo = gh.repository(self.owner, self.name)
        return repo

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
        ordering = ['repo__product_name', 'name']
        
    def get_absolute_url(self):
        return reverse('release_detail', kwargs={'owner': self.owner, 'name': self.name})

    def __unicode__(self):
        return '{}: {}'.format(self.repo.product_name, self.version)
