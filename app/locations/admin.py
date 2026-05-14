from django.contrib import admin

from .models import FavoriteLocation


@admin.register(FavoriteLocation)
class FavoriteLocationAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "nearest_station_name", "added_at")
    search_fields = ("user__username", "user__email", "name", "nearest_station_name")
    list_filter = ("added_at", "admin1")