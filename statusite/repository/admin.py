from django.contrib import admin
from statusite.repository.models import Release
from statusite.repository.models import Repository

class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('repo', 'name', 'beta')
    list_filter = ('repo','beta')
admin.site.register(Release, ReleaseAdmin)

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
admin.site.register(Repository, RepositoryAdmin)
