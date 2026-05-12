from django.urls import path, include
from django.contrib.auth.views import LoginView

from .views import register_view, dashboard_view
from .forms import LoginForm


urlpatterns = [
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),

    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm
        ),
        name="login"
    ),

    path("", include("django.contrib.auth.urls")),
]