from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .models import FavoriteLocation


def parse_float(value):
    """
    Zamienia tekstową współrzędną na float.
    Obsługuje format z kropką i przecinkiem.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None


@login_required
def save_favorite_location(request):
    if request.method != "POST":
        return redirect("air_quality_search")

    name = request.POST.get("name")
    latitude_raw = request.POST.get("latitude")
    longitude_raw = request.POST.get("longitude")
    admin1 = request.POST.get("admin1", "")
    admin2 = request.POST.get("admin2", "")
    nearest_station_id = request.POST.get("nearest_station_id")
    nearest_station_name = request.POST.get("nearest_station_name", "")

    latitude = parse_float(latitude_raw)
    longitude = parse_float(longitude_raw)

    if not name or latitude is None or longitude is None:
        messages.error(request, "Nie udało się zapisać stacji.")
        return redirect("air_quality_search")

    favorite, created = FavoriteLocation.objects.get_or_create(
        user=request.user,
        nearest_station_id=nearest_station_id or None,
        defaults={
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "admin1": admin1,
            "admin2": admin2,
            "nearest_station_name": nearest_station_name,
        }
    )

    if created:
        messages.success(request, f"Dodano stację: {name}")
    else:
        messages.info(request, f"Stacja {name} jest już zapisana.")

    return redirect("my_locations")


@login_required
def my_locations(request):
    locations = FavoriteLocation.objects.filter(
        user=request.user
    ).order_by("-added_at")

    return render(
        request,
        "locations/my_locations.html",
        {
            "locations": locations
        }
    )

@login_required
def delete_favorite_station(request, location_id):
    if request.method != "POST":
        return redirect("my_locations")

    favorite_station = get_object_or_404(
        FavoriteLocation,
        id=location_id,
        user=request.user
    )

    station_name = favorite_station.name
    favorite_station.delete()

    messages.success(request, f"Usunięto stację: {station_name}")

    return redirect("my_locations")