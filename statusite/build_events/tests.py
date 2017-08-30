
import json 
from django.utils import timezone
from django.test import TestCase
# Not sure why these need to be imported this way.
from statusite.repository.models import Release, Repository
from build_events.models import BuildResult
from build_events.serializers import BuildEventSerializer

class TestBuildEvents(TestCase):
    def setUp(self):
        self.repo = Repository(
            owner='Test',
            name='TestRepo', 
            product_name='Test', 
            github_id=1, 
            url='https://example.com/Test/TestRepo'
        )
        self.repo.save()
        self.release = Release(
            repo = self.repo,
            name = 'Version 1',
            version ='Version 1',
            beta = True,
            release_notes = 'Sample Release Notes',
            url = 'https://example.com/Test/TestRepo/releases/tag/uat%2FVersion%201',
            github_id = 100,
            time_created = timezone.now(),
            tag = 'uat/Version 1' 
        )
        self.release.save()


class TestBuildEventSerializer(TestBuildEvents):
    def setUp(self):
        super(TestBuildEventSerializer, self).setUp()
        self.event = {'build_data': {'flow': 'ci_beta'},
                      'build_id': 3000,
                      'plan_name': 'Beta Test',
                      'repository': {'name': 'TestRepo', 'owner': 'Test'},
                      'status': 'Success',
                      'tag': 'uat/Version 1',
                      'tests_failed': 0,
                      'tests_passed': 10,
                      'tests_total': 10,
                      'build_date': timezone.now().date()}

    def test_valid_serializer(self):
        result = BuildEventSerializer(data=self.event)
        self.assertTrue(result.is_valid(), result.errors)
        self.assertEquals(result.validated_data['status'], self.event['status'])

    def test_invalid_repo(self):
        result = BuildEventSerializer(data=self.event)
        result.initial_data['repository']['owner'] = 'forcedotcom'
        self.assertFalse(result.is_valid())
        self.assertIn('repository', result.errors.keys())

    def test_invalid_release(self):
        result = BuildEventSerializer(data=self.event)
        result.initial_data['tag'] = 'uat/Feature 100'
        self.assertFalse(result.is_valid())
        self.assertIn('tag', result.errors.keys())

    def test_serializer_save(self):
        result = BuildEventSerializer(data=self.event)
        self.assertTrue(result.is_valid())
        result.save()
        build = BuildResult.objects.get(repo = self.repo)
        self.assertEqual(build.build_id, 3000)

    def test_serializer_save_update(self):
        result = BuildEventSerializer(data=self.event)
        result.is_valid()
        result.save()
        result2 = BuildEventSerializer(data=self.event)
        result2.initial_data['plan_name'] = 'SUPERFAIL'
        result2.is_valid()
        result2.save()
        count = BuildResult.objects.filter(repo = self.repo, build_id = 3000).count()
        self.assertEqual(1, count)
        build = BuildResult.objects.get(repo = self.repo)
        self.assertEqual('SUPERFAIL', build.plan_name)

class TestBuildReleaseWebhook(TestBuildEvents):
    def test_build_release_webhook(self):
        build_event = {
            'repository': {
                'name': 'TestRepo',
                'owner': 'Test'
            },
            'build': {
                'tag': 'uat/Version 1',
                'plan': 'Upload Beta',
                'id': 3000,
                'status': 'SUCCESS',
                'start_date': timezone.now().date().isoformat(),
                'tests_pass': 10,
                'tests_fail': 0,
                'tests_total': 10
            }
        }
        response = self.client.post('/webhook/mbci/build', json.dumps(build_event), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        build = BuildResult.objects.get(repo = self.repo)
        self.assertEqual(build.build_id, 3000)