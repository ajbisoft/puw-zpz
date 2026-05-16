from django.urls import path
from .views import (
    air_quality_search,
    sensor_history,
    stations_map,
    station_details,
    analytics_dashboard,
    analytics_city,
    analytics_station,
)

urlpatterns = [
    path("", air_quality_search, name="air_quality_search"),
    path("sensor/<int:sensor_id>/history/", sensor_history, name="sensor_history"),
    path("map/", stations_map, name="stations_map"),
    path("station/<int:station_id>/", station_details, name="station_details"),
    path("analytics/", analytics_dashboard, name="analytics_dashboard"),
    path("analytics/city/<str:city_name>/", analytics_city, name="analytics_city"),
    path("analytics/station/<int:station_id>/", analytics_station, name="analytics_station"),
]