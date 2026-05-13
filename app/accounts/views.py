from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import RegisterForm, AccountUpdateForm
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

@login_required
def account_settings_view(request):
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Dane konta zostały zaktualizowane.")
            return redirect("account_settings")
    else:
        form = AccountUpdateForm(instance=request.user)

    return render(
        request,
        "accounts/account_settings.html",
        {
            "form": form
        }
    )