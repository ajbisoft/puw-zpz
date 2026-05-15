from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path

from .models import FavoriteLocation
from air_quality.services.email_alerts import send_air_quality_emails_for_favorite_stations


@admin.register(FavoriteLocation)
class FavoriteLocationAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "nearest_station_name", "added_at")
    search_fields = ("user__username", "user__email", "name", "nearest_station_name")
    list_filter = ("added_at", "admin1")

    change_list_template = "admin/locations/favoritelocation/change_list.html"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "send-air-quality-emails/",
                self.admin_site.admin_view(self.send_air_quality_emails),
                name="favorite_locations_send_air_quality_emails",
            ),
        ]

        return custom_urls + urls

    def send_air_quality_emails(self, request):
        try:
            sent_count = send_air_quality_emails_for_favorite_stations()

            messages.success(
                request,
                f"Wysłano powiadomienia e-mail: {sent_count}."
            )

        except Exception as error:
            messages.error(
                request,
                f"Nie udało się wysłać powiadomień e-mail: {error}"
            )

        return redirect("..")