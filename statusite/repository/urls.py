from django.conf.urls import url

from statusite.repository import views as repository_views

urlpatterns = [
    url(r'webhook/github/release$', repository_views.github_release_webhook, name="github_release_webhook"),
    url(r'(?P<owner>\w+)/(?P<name>[^/].*)/*$', repository_views.repo_detail, name="repo_detail"),
]
