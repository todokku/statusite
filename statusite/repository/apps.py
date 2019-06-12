from __future__ import unicode_literals

from django.apps import AppConfig


class RepositoryConfig(AppConfig):
    name = "statusite.repository"

    def ready(self):
        # side-effect import to register handler
        import statusite.repository.handlers  # noqa
