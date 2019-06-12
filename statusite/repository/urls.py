from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers
from statusite.repository import views as repository_views

router = routers.DefaultRouter()
# router.register(r'repos', repository_views.ApiRepository)

app_name = 'repository'
urlpatterns = [
    # url(r'^', include(router.urls)),
    url(
        r"webhook/github/release$",
        repository_views.github_release_webhook,
        name="github_release_webhook",
    ),
    url(
        r"(?P<owner>\w+)/(?P<name>[^/].*)/*$",
        repository_views.repo_detail,
        name="repository-detail",
    ),
    url(
        r"(?P<owner>\w+)/(?P<name>[^/].*)/*$",
        repository_views.repo_detail,
        name="release-detail",
    ),
]
