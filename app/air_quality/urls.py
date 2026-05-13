from django.urls import path
from .views import air_quality_search, sensor_history

urlpatterns = [
    path("", air_quality_search, name="air_quality_search"),
    path("sensor/<int:sensor_id>/history/", sensor_history, name="sensor_history"),
]