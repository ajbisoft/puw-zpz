# puw-zpz
### Platforma wizualizująca dane ze stacji czujników IoT z mapą i statystykami.

# Jak uruchomić aplikację?

## Wymagania

Aby uruchomić aplikację, trzeba mieć zainstalowanego Pythona, najlepiej 3.10. 

---

## Kroki uruchomienia

### 1. Przejdź do katalogu aplikacji

```bash
cd app
```

> Jeśli katalog projektu ma inną nazwę, przejdź do katalogu, w którym znajduje się plik `manage.py`.

---

### 2. Utwórz środowisko wirtualne

```bash
python -m venv venv
```

---

### 3. Aktywuj środowisko wirtualne

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

---

### 4. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

---

### 5. Skonfiguruj plik `.env`

Utwórz lub edytuj plik `.env` w katalogu głównym projektu, czyli tam, gdzie znajduje się `manage.py`.

Przykładowa zawartość pliku `.env`:

```env
EMAIL_HOST_USER=twoj_adres@gmail.com
EMAIL_HOST_PASSWORD=wygenerowane_haslo_aplikacji
```

Hasło aplikacji Google można wygenerować pod adresem:

```text
https://myaccount.google.com/apppasswords
```

Dzięki temu możliwe będzie automatyczne wysyłanie powiadomień e-mail o jakości powietrza.

---

### 6. Wykonaj migracje bazy danych

```bash
python manage.py migrate
```

---

### 7. Opcjonalnie pobierz dane z API GIOŚ

Import ograniczony (przydatny do szybkiego testu):

```bash
python manage.py import_gios_data --limit 50
```

Pełny import danych (zalecany, ale może potrwać około 5 minut):

```bash
python manage.py import_gios_data
```

---

### 8. Uruchom aplikację

```bash
python manage.py runserver
```

Aplikacja będzie dostępna pod adresem:

```text
http://127.0.0.1:8000/
```

---

## Panel administratora

Aby utworzyć konto administratora, użyj polecenia:

```bash
python manage.py createsuperuser
```

Następnie wejdź na:

```text
http://127.0.0.1:8000/admin/
```

W panelu administratora można zarządzać użytkownikami, stacjami, czujnikami, pomiarami oraz uruchamiać pobieranie danych i wysyłkę powiadomień e-mail.