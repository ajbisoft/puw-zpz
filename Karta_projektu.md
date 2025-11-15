# KARTA PROJEKTU

## 1. Informacje ogólne

**Tytuł projektu:**  
System monitorowania jakości powietrza - Platforma wizualizująca dane ze stacji czujników IoT z mapą i statystykami  

**Akronim projektu:** SMJP  
**Data utworzenia:** 19.10.2025  
**Wersja dokumentu:** 1.0  

**Zespół projektowy:**

| Imię i nazwisko     | Rola w projekcie                     | Zakres odpowiedzialności |
|----------------------|--------------------------------------|---------------------------|
| Jakub Kwiatkowski    | Kierownik projektu, Architekt        | Planowanie, koordynacja projektu, definicja architektury systemu |
| Jakub Janusz         | Full Stack Developer                 | Implementacja backendu i frontendu, integracja danych |
| Monika Korniak       | Data Analyst, Stakeholder            | Analiza i wizualizacja danych, współtworzenie modułu frontendu, kontrola wymagań merytorycznych i użytkowych

**Prowadzący:** mgr Wojciech Moniuszko  
**Jednostka dydaktyczna:** Wyższa Szkoła Przedsiębiorczości i Administracji w Lublinie  

---

## 2. Cel projektu

Projekt zakłada stworzenie interaktywnej platformy internetowej, która będzie gromadzić, przetwarzać i wizualizować dane o jakości powietrza pochodzące z czujników IoT.  
System ma umożliwiać użytkownikom śledzenie parametrów środowiskowych na mapie oraz analizę trendów i statystyk historycznych.

Aplikacja będzie pobierać dane z zewnętrznych źródeł (API meteorologiczne i symulacja danych z czujników) i prezentować je w przystępny sposób – w postaci dashboardu, mapy cieplnej, wykresów oraz raportów dziennych.

---

## 3. Uzasadnienie projektu

Stworzenie platformy do monitorowania jakości powietrza w czasie rzeczywistym pozwoli użytkownikom podejmować bardziej świadome decyzje (np. dotyczące aktywności na świeżym powietrzu).  

Obecnie brakuje jednej, centralnej i przejrzystej platformy przedstawiającej dane dotyczące jakości powietrza. Projekt SMJP ma to zmienić, zwiększając świadomość ekologiczną i efektywność zarządzania informacją dotyczącą środowiska.

---

## 4. Zakres projektu

**W zakresie projektu:**

- Opracowanie wymagań funkcjonalnych i niefunkcjonalnych  
- Zaprojektowanie systemu z wykorzystaniem UML 
- Integracja z API symulującym dane z czujników IoT 
- Implementacja aplikacji webowej (backend, frontend, baza danych)  
- Moduł wykresów i statystyk 
- Dokumentacja projektowa i techniczna  
- Testy i prezentacja prototypu  

**Poza zakresem projektu:**
- Fizyczna instalacja czujników IoT  


---


## 5. Wymagania

| Typ | Opis |
|------|------|
| **Funkcjonalne** | Gromadzenie i zapisywanie danych środowiskowych w bazie danych |
| **Funkcjonalne** | Prezentacja danych w formie wykresów i raportów |
| **Funkcjonalne** | Możliwość filtrowania danych według lokalizacji, zakresu dat oraz typu parametru |
| **Niefunkcjonalne** | Wydajność: maksymalny czas ładowania dashboardu i wizualizacji ≤ 5 sekund. |
| **Niefunkcjonalne** | Dostępność: system dostępny przez minimum 99% czasu działania. |
| **Niefunkcjonalne** | Responsywność: interfejs dostosowany do urządzeń desktopowych |
| **Interfejsowe** | Przeglądarkowy interfejs użytkownika w technologii HTML5, CSS3, JS |

---

## 6. Zespół projektowy i role

| Rola | Osoba | Odpowiedzialność |
|------|--------|------------------|
| **Project Manager, Architekt** | Jakub Kwiatkowski | Planowanie i koordynacja prac zespołu, definiowanie architektury systemu, nadzór nad projektem |
| **Full Stack Developer** | Jakub Janusz | Implementacja backendu i frontendu aplikacji, integracja z API zewnętrznymi, utrzymanie środowiska projektowego. |
| **Data Analyst, Stakeholder** | Monika Korniak | Analiza i wizualizacja danych, współtworzenie modułu frontendu w zakresie dashboardu i wykresów, kontrola wymagań merytorycznych  |


---

## 7. Zasoby i narzędzia

| Kategoria | Narzędzie / Technologia | Cel zastosowania |
|------------|--------------------------|------------------|
| Zarządzanie projektem | Azure DevOps| Planowanie sprintów, śledzenie zadań |
| Repozytorium | GitHub | Kontrola wersji kodu |
| Analiza i projektowanie | Mermaid | Diagramy UML, mockupy interfejsu |
| Backend | Python | Logika przetwarzania danych i API |
| Frontend | Bootstrap | Interaktywny interfejs webowy |
| Baza danych | MySQL/SQL lite | Przechowywanie danych historycznych |
| Wizualizacja danych | Bootstrap | Wykresy, mapy, trendy, statystyki |
| Komunikacja | Discord | Spotkania, wymiana informacji |

---

## 8. Harmonogram realizacji (10 spotkań)

| Etap | Zakres | Czas realizacji | Rezultat |
|------|--------|-----------------|-----------|
| 1 | Tworzenie zespołów, wybór tematu, karta projektu | Tydzień 1 | Karta projektu |
| 2 | Analiza wymagań | Tydzień 2 | Dokument wymagań |
| 3 | Projekt systemu - UML | Tydzień 3–4 | Diagramy UML |
| 4 | Konfiguracja środowiska | Tydzień 4 | Repozytorium, narzędzia |
| 5 | Dokumentacja projektowa (I etap) | Tydzień 5 | Wstępna dokumentacja |
| 6 | Implementacja prototypu (I etap) | Tydzień 6–7 | Pierwsza wersja aplikacji |
| 7 | Testowanie i poprawki | Tydzień 8 | Raport testów |
| 8 | Dokumentacja końcowa i prezentacja | Tydzień 9–10 | Prezentacja, protokół odbioru |

---

## 9. Analiza ryzyka

| Nr | Ryzyko | Prawdopodobieństwo | Skutek | Działanie zapobiegawcze |
|----|--------|--------------------|---------|--------------------------|
| 1 | Opóźnienia w pracy zespołu | Średnie | Wysoki | Spotkania statusowe, śledzenie postępów w Azure DevOps |
| 2 | Konflikty w zespole | Niskie | Średni | Jasny podział ról, komunikacja na Discord |
| 3 | Utrata danych w repozytorium | Niskie | Wysoki | Regularne kopie GitHub, lokalne backupy |
| 4 | Niedostarczenie dokumentacji | Niskie | Wysoki | Wczesne rozpoczęcie, przeglądy postępów |
| 5 | Brak połączenia z internetem / przekoczenie liczby zapytań API | Wysokie | Wysoki | Przetrzymywanie danych historycznych w bazie danych |

---

## 10. Kryteria sukcesu projektu

- Wszystkie wymagania funkcjonalne zaimplementowane (dashboard zawierający mapę i wykresy)  
- Aplikacja działa lokalnie, poprawnie pobiera dane z API  
- Dokumentacja zawiera pełny zestaw diagramów UML i opis architektury  
- Testy akceptacyjne zakończone wynikiem pozytywnym  
- Projekt ukończony w wyznaczonym czasie  
- Projekt pozytywnie oceniony przez prowadzącego  

---

## 11. Rezultaty projektu

- Prototyp aplikacji webowej (SMJP) dostępny w repozytorium  
- Dokumentacja projektowa (wymagania, UML, plan testów)  
- Dokumentacja techniczna  
- Prezentacja zespołowa (PowerPoint / PDF)  
- Raport końcowy i protokół zdawczo-odbiorczy  

---

## 12. Akceptacja projektu

| Funkcja | Imię i nazwisko | Data | Podpis |
|----------|------------------|-------|---------|
| Kierownik projektu | Jakub Kwiatkowski | 19.10.2025 | ___________ |
| Prowadzący | mgr Wojciech Moniuszko | 19.10.2025 | ___________ |

---

### Uwagi końcowe
- Dokument przechowywany w repozytorium projektu  
- Aktualizacja wersji wymaga zgody kierownika projektu i prowadzącego  
- Każdy członek zespołu ma obowiązek zapoznać się z treścią karty i ją zaakceptować
