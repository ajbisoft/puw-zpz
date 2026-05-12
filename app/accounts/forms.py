from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Adres e-mail"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Nazwa użytkownika",
            "email": "Adres e-mail",
            "password1": "Hasło",
            "password2": "Powtórz hasło",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nazwa użytkownika"
        self.fields["password1"].label = "Hasło"
        self.fields["password2"].label = "Powtórz hasło"

        for field in self.fields.values():
            field.help_text = ""
            field.widget.attrs.update({
                "class": "form-control"
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nazwa użytkownika",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Podaj nazwę użytkownika"
        })
    )

    password = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Podaj hasło"
        })
    )