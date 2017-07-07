from statusite.repository.models import Release
from statusite.repository.models import Repository
from rest_framework import serializers

class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ('name', 'version', 'beta', 'release_notes', 'url', 'time_created')

class RepositorySerializer(serializers.ModelSerializer):
    latest_release = ReleaseSerializer(required=False)
    latest_beta = ReleaseSerializer(required=False)
    class Meta:
        model = Repository
        fields = ('name', 'owner', 'product_name', 'github_id', 'url', 'latest_release', 'latest_beta')
