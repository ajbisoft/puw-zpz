from django.urls import path
from .views import air_quality_search

urlpatterns = [
    path("", air_quality_search, name="air_quality_search"),
]