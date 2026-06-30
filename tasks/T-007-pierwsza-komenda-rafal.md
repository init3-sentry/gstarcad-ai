# T-007 — Pierwsza własna komenda: WYCZYŚĆ_NIEUŻYWANE (Rafał Trzusło)

| Pole | Wartość |
|---|---|
| Identyfikator | T-007 |
| Etap | pierwszy |
| Przypisany do | **Rafał Trzusło** |
| Przewidywany czas | 8 godzin |
| Status | oczekuje |
| Data wejścia | 2026-07-15 |
| Data deklarowanego ukończenia | 2026-07-25 |
| Zależy od | T-003 (Rafał przeszedł wprowadzenie) |

## Cel

Napisanie własnej komendy **WYCZYŚĆ_NIEUŻYWANE**, która usuwa z bieżącego rysunku wszystkie nieużywane elementy — warstwy bez obiektów, definicje bloków, do których nie ma odniesienia, style tekstu i wymiarowania, do których nie ma odniesienia. Po wykonaniu komenda raportuje, ile elementów każdego typu zostało usuniętych.

To jest typowe narzędzie kontrolne, którego klienci pytają regularnie i które zdecydowanie ma popyt. Dla Rafała jest to też świetne ćwiczenie w zakresie pracy z różnymi tabelami symboli GstarCAD-a.

## Kryteria akceptacji

- [ ] Plik `przyklady-chlopcow/rafal/wyczysc_nieuzywane.py` istnieje w gałęzi roboczej
- [ ] Komenda zarejestrowana jako `WYCZYŚĆ_NIEUŻYWANE` po załadowaniu poleceniem `APPLOAD`
- [ ] Komenda działa poprawnie na rysunku testowym (Dawid przygotuje rysunek z celowo dodanymi nieużywanymi warstwami, blokami i stylami)
- [ ] Po wykonaniu wyświetla komunikat: „Usunięto X warstw, Y bloków, Z stylów tekstu, W stylów wymiarowania"
- [ ] Plik `README.md` z opisem komendy w polskim
- [ ] Dwa zrzuty ekranu pokazujące rysunek przed i po wykonaniu komendy

## Wskazówki techniczne

Klucz to bezpieczne sprawdzenie, czy element jest faktycznie nieużywany przed jego usunięciem. GstarCAD ma wbudowane polecenie `_PURGE` z mechanizmem sprawdzania, ale tu chodzi o własną komendę w Pythonie, która daje dodatkowe informacje (raport).

Dla pomocnika dobrym zapytaniem startowym jest: „Napisz komendę GstarCAD-a w Pythonie, która iteruje po wszystkich tabelach symboli rysunku — warstwach, blokach, stylach tekstu i wymiarowania — i dla każdej iteruje po jej rekordach. Dla każdego rekordu sprawdza, czy istnieją do niego odniesienia w rysunku. Jeśli nie — usuwa go i zlicza. Na końcu wyświetla raport z liczbami usuniętych elementów. Komenda nazywa się `WYCZYŚĆ_NIEUŻYWANE`."

## Materiały odniesienia

Te same co T-005.
