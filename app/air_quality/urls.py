from django.urls import path
from .views import air_quality_search, sensor_history, stations_map, station_details

urlpatterns = [
    path("", air_quality_search, name="air_quality_search"),
    path("sensor/<int:sensor_id>/history/", sensor_history, name="sensor_history"),
    path("map/", stations_map, name="stations_map"),
    path("station/<int:station_id>/", station_details, name="station_details"),
]