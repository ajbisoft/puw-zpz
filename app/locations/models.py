from django.conf import settings
from django.db import models


class FavoriteLocation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_locations"
    )

    name = models.CharField(max_length=255)

    latitude = models.FloatField()
    longitude = models.FloatField()

    admin1 = models.CharField(max_length=255, blank=True, null=True)
    admin2 = models.CharField(max_length=255, blank=True, null=True)

    nearest_station_id = models.IntegerField(blank=True, null=True)
    nearest_station_name = models.CharField(max_length=255, blank=True, null=True)

    custom_alias = models.CharField(max_length=100, blank=True, null=True)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "latitude", "longitude")

    def __str__(self):
        return f"{self.name} - {self.user}"