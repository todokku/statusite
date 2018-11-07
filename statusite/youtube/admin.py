from django.contrib import admin

from statusite.youtube.models import Playlist


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("title", "youtube_id")


admin.site.register(Playlist, PlaylistAdmin)
