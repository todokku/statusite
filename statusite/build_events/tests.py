
import json 
from django.utils import timezone
from django.test import TestCase

from rest_framework.test import APIRequestFactory, APIClient

# Not sure why these need to be imported this way.
from statusite.repository.models import Release, Repository
from build_events.models import BuildResult
from build_events.serializers import BuildEventSerializer
from build_events.views import BuildEventWebhook

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

class TestBuildEventWebhookView(TestBuildEvents):
    def test_create_webhook(self):
        factory = APIRequestFactory()
        request = factory.post('/url', self.event, format='json')
        view = BuildEventWebhook.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 201)


class TestBuildEventSerializer(TestBuildEvents):

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

class TestBuildEventWebhook(TestBuildEvents):
    def test_webhook_call(self):
        self.client = APIClient()
        build_event = {
            'repository': {
                'name': 'TestRepo',
                'owner': 'Test'
            },
            'tag': 'uat/Version 1',
            'plan_name': 'Beta Build',
            'build_id': 3000,
            'status': 'SUCCESS',
            'build_date': timezone.now().date().isoformat(),
            'tests_passed': 10,
            'tests_failed': 0,
            'tests_total': 10,
            'build_data': {'flow': 'ci_beta'}
        }
        response = self.client.post('/webhook/mbci', json.dumps(build_event), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        build = BuildResult.objects.get(repo = self.repo)
        self.assertEqual(build.build_id, 3000)
