from django.conf import settings
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver
from github3 import login
from statusite.repository.models import Repository

@receiver(pre_save, sender=Repository)
def set_github_id(sender, **kwargs):
    repository = kwargs['instance']

    if not repository.github_id:
        github = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
        repo = github.repository(repository.owner, repository.name)
        repository.github_id = repo.id
        repository.save()

@receiver(post_save, sender=Repository)
def create_repo_webhooks(sender, **kwargs):
    # Skip updates
    if not kwargs['created']:
        return

    repo = kwargs['instance']
    event = 'release'

    callback_url = '{}/repo/{}'.format(settings.GITHUB_WEBHOOK_BASE_URL, event)
  
    # Initialize repo API 
    github = repo.github_api

    # Check if webhook exists for repo
    existing = False
    for hook in github.iter_hooks():
        if hook.config.get('url') == callback_url and event in hook.events:
            existing = True

    # If no webhook, create it 
    if not existing:
        kwargs = {
            'name': 'web',
            'events': [event],
            'config': {
                'url': callback_url,
                'content_type': 'json',
                'secret': settings.GITHUB_WEBHOOK_SECRET,
            },
        }
        resp = github.create_hook(**kwargs)

        return resp
