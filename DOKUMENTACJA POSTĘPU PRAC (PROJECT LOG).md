# DOKUMENTACJA POSTĘPU PRAC (PROJECT LOG)

**Projekt:** System Monitorowania Jakości Powietrza (SMJP)  
**Data utworzenia:** 15.05.2026  
**Zespół:** 
*   **Jakub Kwiatkowski** (Kierownik projektu, Architekt)
*   **Jakub Janusz** (Full Stack Developer)
*   **Monika Korniak** (Data Analyst, Stakeholder)

---

## Dziennik Spotkań i Kamienie Milowe

### 1. Spotkanie Inicjalizujące
**Data:** 29.04.2026  
**Cel:** Podział ról i start projektu.

*   **MK:** Opracowanie struktury bazy danych w `SQLite` oraz analiza endpointów API GIOŚ.
*   **JJ:** Konfiguracja środowiska pod framework `Django` i przygotowanie fundamentów backendu.

---

### 2. Przegląd i Retrospekcja (Moment zwrotny)
**Data:** 06.05.2026  
**Status:** Krytyczny

> **Lessons Learned:** Pierwszy przegląd wykazał całkowity brak postępu przez błędy w komunikacji (nikt nie wiedział, od czego zacząć). 
> 
> **Działania:** Przeprowadzono "szczerą rozmowę" zespołową. Wyjaśniono wątpliwości i ustalono jasny model współpracy. Od teraz działamy jako zgrany zespół.

---

### 3. Status Realizacji – Etap I
**Data:** 10.05.2026  

*   Zatwierdzono ostateczne API oraz strukturę tabel w bazie danych.
*   Szkielet aplikacji Django został zainicjowany.

---

### 4. Weryfikacja Jakościowa
**Data:** 13.05.2026  
**Status:** Poprawki wdrożone

*   Deweloper zgłosił gotowość szkieletu. 
*   **Wykryty błąd:** Po analizie (MK) okazało się, że brakuje **danych historycznych**, które są kluczowe dla wykresów statystycznych.
*   **Decyzja:** Zwrot zadania do dewelopera w celu rozszerzenia logiki pobierania danych.

---

### 5. Raport Bieżący
**Data:** 15.05.2026  
**Status:** Zakończony

*   **Backend:** Szkielet gotowy, dane historyczne są już poprawnie pobierane do bazy.
*   **Analityka:** Rozpoczęto prace nad modułem wizualizacji (wykresy, trendy).
*   **QA:** Trwa review logiki biznesowej pod kątem zgodności z wymaganiami.


### 6. Spotkanie 17.05.2026
**Status:** Aktywny

*   **Uwaga:** Spotkanie fizyczne nie odbyło się, ustalenia zostały podjęte drogą pisemną.
*   **Analityka & QA:** Moduł analityczny został zakończony, a logika biznesowa pomyślnie zweryfikowana.
*   **Wykryty problem / Optymalizacja:** Zauważono potrzebę optymalizacji procesu pobierania danych.
*   **Decyzja:** Wprowadzenie ograniczenia pobierania danych wyłącznie do 5 kluczowych wskaźników (rezygnacja z analizy pozostałych parametrów w celu zwiększenia wydajności systemu).
  

### 7. Przegląd Stanu Aktualnego
**Data spotkania:** 27.05.2026  
**Status (na dzień 30.05.2026):** Wdrożone

*   **Optymalizacja:** Zgodnie z wcześniejszymi ustaleniami pisemnymi, wdrożono ograniczenie pobierania danych.
*   **Efekt:** System pobiera teraz wyłącznie 5 kluczowych wskaźników, co pozwoliło na optymalizację działania bazy danych i aplikacji.

---



*Wdrożona dokumentacja powinna być aktualizowana po każdym spotkaniu statusowym/ etapie prac*
