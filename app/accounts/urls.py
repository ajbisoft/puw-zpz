from django.urls import path, include
from django.contrib.auth.views import LoginView, PasswordChangeView

from .views import register_view, dashboard_view, account_settings_view
from .forms import LoginForm, BootstrapPasswordChangeForm


urlpatterns = [
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("settings/", account_settings_view, name="account_settings"),

    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm
        ),
        name="login"
    ),

    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            form_class=BootstrapPasswordChangeForm,
            success_url="/accounts/password_change/done/"
        ),
        name="password_change"
    ),

    path("", include("django.contrib.auth.urls")),
]