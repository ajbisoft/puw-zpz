from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm
from locations.models import FavoriteLocation


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard_view(request):
    favorite_locations = FavoriteLocation.objects.filter(
        user=request.user
    ).order_by("-added_at")

    return render(
        request,
        "accounts/dashboard.html",
        {
            "favorite_locations": favorite_locations
        }
    )