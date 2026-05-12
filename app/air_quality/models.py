from django.db import models


class Station(models.Model):
    gios_id = models.IntegerField(unique=True)

    station_code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    latitude = models.FloatField()
    longitude = models.FloatField()

    city_name = models.CharField(max_length=255)
    commune = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.city_name})"


class Sensor(models.Model):
    gios_id = models.IntegerField(unique=True)

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="sensors"
    )

    param_name = models.CharField(max_length=100)
    param_code = models.CharField(max_length=50)
    param_formula = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.param_code} - {self.station.name}"


class Measurement(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="measurements"
    )

    timestamp = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ("sensor", "timestamp")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.sensor.param_code}: {self.value} at {self.timestamp}"


class AQINorm(models.Model):
    param_code = models.CharField(max_length=50)
    index_level = models.CharField(max_length=100)

    min_value = models.FloatField()
    max_value = models.FloatField()

    color_hex = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.param_code} - {self.index_level}"