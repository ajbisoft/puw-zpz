from django.urls import path

from .views import save_favorite_location, my_locations, delete_favorite_station


urlpatterns = [
    path("save/", save_favorite_location, name="save_favorite_location"),
    path("my/", my_locations, name="my_locations"),
    path("delete/<int:location_id>/", delete_favorite_station, name="delete_favorite_station"),
]