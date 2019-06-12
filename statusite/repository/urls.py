from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers
from statusite.repository import views as repository_views

router = routers.DefaultRouter()

app_name = "repository"
urlpatterns = [
    url(
        r"webhook/github/release$",
        repository_views.github_release_webhook,
        name="github_release_webhook",
    )
]
