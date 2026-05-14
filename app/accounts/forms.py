from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm


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

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email:
            email = email.strip().lower()

            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError(
                    "Konto z tym adresem e-mail już istnieje."
                )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()

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

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": "Nazwa użytkownika",
            "email": "Adres e-mail",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Nazwa użytkownika"
        })

        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Adres e-mail"
        })

class BootstrapPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].label = "Obecne hasło"
        self.fields["new_password1"].label = "Nowe hasło"
        self.fields["new_password2"].label = "Powtórz nowe hasło"

        self.fields["old_password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Wpisz obecne hasło"
        })

        self.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Wpisz nowe hasło"
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Powtórz nowe hasło"
        })

        for field in self.fields.values():
            field.help_text = ""