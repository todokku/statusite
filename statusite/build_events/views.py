from rest_framework.generics import CreateAPIView
from build_events.serializers import BuildEventSerializer

class BuildEventWebhook(CreateAPIView):
    serializer_class = BuildEventSerializer
