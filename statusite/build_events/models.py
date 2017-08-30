from django.db import models
from jsonfield import JSONField

class BuildResult(models.Model):
    class Meta:
        verbose_name = 'Build Result'

    repo = models.ForeignKey('repository.Repository', related_name='build_results')
    release = models.ForeignKey('repository.Release', related_name='build_results')
    plan_name = models.CharField(max_length=255)
    build_id = models.IntegerField('mrbelvedereci build id')
    status = models.CharField(max_length=25)
    build_date = models.DateField()
    tests_passed = models.IntegerField()
    tests_failed = models.IntegerField()
    tests_total = models.IntegerField()
    build_data = JSONField(blank=True)
    # TODO: additional build stats

    def __str__(self):
        return '{}: {} [Build {}]'.format(self.repo.product_name, 1, self.build_id)

