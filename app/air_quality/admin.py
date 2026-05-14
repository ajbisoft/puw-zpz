from django.contrib import admin, messages
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import path

from .models import Station, Sensor, Measurement, AQINorm
from air_quality.services.email_alerts import send_air_quality_emails_for_favorite_stations

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "city_name", "province", "gios_id")
    search_fields = ("name", "city_name", "province")
    list_filter = ("province",)

    change_list_template = "admin/air_quality/station/change_list.html"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "import-gios-all/",
                self.admin_site.admin_view(self.import_gios_all),
                name="import_gios_all",
            ),
            path(
                "send-air-quality-emails/",
                self.admin_site.admin_view(self.send_air_quality_emails),
                name="send_air_quality_emails",
            ),
        ]

        return custom_urls + urls

    def import_gios_all(self, request):
        try:
            messages.info(
                request,
                "Rozpoczęto pobieranie danych ze wszystkich stacji GIOŚ. To może chwilę potrwać."
            )

            call_command(
                "import_gios_data",
                sleep=0.1,
            )

            messages.success(
                request,
                "Zakończono pobieranie danych GIOŚ. Jeśli zapisano nowe pomiary, powiadomienia e-mail zostały wysłane."
            )

        except Exception as error:
            messages.error(
                request,
                f"Wystąpił błąd podczas pobierania danych GIOŚ: {error}"
            )

        return redirect("..")

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


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("param_code", "param_name", "station", "gios_id")
    search_fields = ("param_code", "param_name", "station__name")
    list_filter = ("param_code",)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("sensor", "timestamp", "value")
    search_fields = ("sensor__param_code", "sensor__station__name")
    list_filter = ("sensor__param_code", "timestamp")


@admin.register(AQINorm)
class AQINormAdmin(admin.ModelAdmin):
    list_display = ("param_code", "index_level", "min_value", "max_value", "color_hex")
    search_fields = ("param_code", "index_level")
    list_filter = ("param_code", "index_level")