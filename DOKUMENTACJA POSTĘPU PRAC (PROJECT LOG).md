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
**Status:** Aktywny

*   **Backend:** Szkielet gotowy, dane historyczne są już poprawnie pobierane do bazy.
*   **Analityka:** Rozpoczęto prace nad modułem wizualizacji (wykresy, trendy).
*   **QA:** Trwa review logiki biznesowej pod kątem zgodności z wymaganiami.

#### UWAGA: Zaplanowane spotkanie statusowe: 17.05.2026


---



*Wdrożona dokumentacja powinna być aktualizowana po każdym spotkaniu statusowym/ etapie prac*
