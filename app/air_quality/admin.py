from django.contrib import admin
from .models import Station, Sensor, Measurement, AQINorm


admin.site.register(Station)
admin.site.register(Sensor)
admin.site.register(Measurement)
admin.site.register(AQINorm)