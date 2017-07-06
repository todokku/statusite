import hmac
import json
import re

import dateutil.parser
from hashlib import sha1

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from statusite.repository.models import Release
from statusite.repository.models import Repository

def repo_list(request, owner=None):
    repos = Repository.objects.all()

    context = {
        'repos': repos,
    }
    return render(request, 'repository/repo_list.html', context=context)

def repo_detail(request, owner, name):
    query = {
        'owner': owner,
        'name': name,
    }
    repo = get_object_or_404(Repository, **query)

    context = {
        'repo': repo,
    }
    return render(request, 'repository/repo_detail.html', context=context)

def validate_github_webhook(request):
    key = settings.GITHUB_WEBHOOK_SECRET
    signature = request.META.get('HTTP_X_HUB_SIGNATURE').split('=')[1]
    mac = hmac.new(bytearray(key, 'utf8'), msg=request.body, digestmod=sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return False
    return True

@csrf_exempt
@require_POST
def github_release_webhook(request):
    if not validate_github_webhook(request):
        return HttpResponseForbidden

    release_event = json.loads(request.body.decode('utf-8')) 
    print(release_event)

    repo_id = release_event['repository']['id']
    try:
        repo = Repository.objects.get(github_id = repo_id)
    except Repository.DoesNotExist:
        return HttpResponse('Not listening for this repository')

    time_created = dateutil.parser.parse(release_event['release']['created_at'])
  
    release = Release(
        repo = repo,
        name = release_event['release']['name'],
        version = release_event['release']['name'],
        beta = release_event['release']['prerelease'],
        release_notes = release_event['release']['body'],
        url = release_event['release']['html_url'],
        github_id = release_event['release']['id'],
        time_created = time_created,
    ) 
    release.save()

    return HttpResponse('OK')
