from django.contrib import admin

from build_events.models import BuildResult

# Register your models here.
class BuildResultAdmin(admin.ModelAdmin):
    list_display = ('repo','release','plan_name','status')
admin.site.register(BuildResult, BuildResultAdmin)