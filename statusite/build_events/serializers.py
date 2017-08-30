from rest_framework import serializers
from build_events.models import BuildResult
from statusite.repository.models import Repository, Release

# these two serializers are for webhook deserialization


class BuildEventRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ('name', 'owner')


class BuildEventSerializer(serializers.ModelSerializer):
    """ Converts a BuildEvent into a BuildResult """
    repository = BuildEventRepositorySerializer(source='repo') # setting source renames it after validation, I guess
    tag = serializers.CharField(max_length=255, write_only=True)
    build_data = serializers.JSONField()

    class Meta:
        model = BuildResult
        fields = ('plan_name', 'build_id', 'status', 'tests_passed', 'build_date',
                  'tests_failed', 'tests_total', 'build_data', 'repository', 'tag')

    def save(self, **kwargs):
        
        # if this is actually an update, set an instance.
        try:
            self.instance = self.validated_data['release'].build_results.get(
                build_id = self.validated_data['build_id'
            ])
        except BuildResult.DoesNotExist:
            pass

        super(BuildEventSerializer, self).save(**kwargs)

    def validate_repository(self, repo):
        try:
            repository = Repository.objects.get(owner=repo['owner'], name=repo['name'])
        except Repository.DoesNotExist:
            raise serializers.ValidationError(
                "The repository {}/{} did not exist.".format(repo['owner'], repo['name'])
            )

        return repository

    def validate(self, data):
        tag_name = data.pop('tag')

        try:
            data['release'] = data['repo'].releases.get(
                tag = tag_name
            )
        except Release.DoesNotExist:
            raise serializers.ValidationError({
                'tag': "The release {} does not exist".format(tag_name)
            })

        return data
