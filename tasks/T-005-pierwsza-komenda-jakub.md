# T-005 — Pierwsza własna komenda: BATCH_EXPORT_PDF_WARSTWAMI (Jakub Moszko)

| Pole | Wartość |
|---|---|
| Identyfikator | T-005 |
| Etap | pierwszy |
| Przypisany do | **Jakub Moszko** |
| Przewidywany czas | 8 godzin (rozłożone na cały tydzień) |
| Status | oczekuje |
| Data wejścia | 2026-07-15 |
| Data deklarowanego ukończenia | 2026-07-25 |
| Zależy od | T-001 (Jakub przeszedł wprowadzenie) |

## Cel

Napisanie pierwszej własnej komendy GstarCAD-a w Pythonie — w pełni samodzielnie, przy pomocy pomocnika „GstarCAD Python Helper" (na skonfigurowanym koncie ChatGPT Team), z weryfikacją w GstarCAD 2026. Komenda nazywa się **BATCH_EXPORT_PDF_WARSTWAMI** i eksportuje każdą warstwę bieżącego rysunku do osobnego pliku PDF, z numerem warstwy w nazwie pliku.

## Kryteria akceptacji

- [ ] Plik `przyklady-chlopcow/jakub/batch_export_pdf_warstwami.py` istnieje w gałęzi roboczej w repozytorium
- [ ] Plik zawiera dekorator `@command` rejestrujący komendę pod nazwą `BATCH_EXPORT_PDF_WARSTWAMI`
- [ ] Po załadowaniu poleceniem `APPLOAD` komenda jest dostępna w command line GstarCAD 2026
- [ ] Komenda działa poprawnie na rysunku testowym dostarczonym przez Dawida (`materialy-testowe/rysunek-testowy-warstwy.dwg`)
- [ ] W tym samym katalogu znajduje się plik `README.md` z opisem komendy, instrukcją uruchomienia i przewidywanym efektem działania, w pięknym polskim
- [ ] Dwa zrzuty ekranu pokazujące działanie komendy w GstarCAD-zie zapisane w katalogu komendy

## Wskazówki techniczne

Komenda będzie używać następujących elementów pygcad (skrót — pełna referencja w przewodniku systemowym):

- `pygcad.pygrx.gcdbHostApplicationServices().workingDatabase()` — uchwyt aktualnego rysunku
- `pygcad.pygrx.GcDbLayerTableRecord` — odczyt warstw rysunku
- polecenie `_PLOT` z odpowiednim mapowaniem warstw do różnych zestawów wyboru (sterowanie widocznością przed eksportem)

Dla pomocnika dobrym zapytaniem startowym jest: „Napisz komendę GstarCAD-a w Pythonie, która iteruje po wszystkich warstwach bieżącego rysunku, włącza widoczność tylko jednej warstwy na raz, eksportuje aktualny widok do pliku PDF nazwanego po identyfikatorze tej warstwy, i przechodzi do następnej. Komenda nazywa się `BATCH_EXPORT_PDF_WARSTWAMI` i używa dekoratora `@command()`."

Pierwsza odpowiedź pomocnika prawdopodobnie nie będzie idealna. To jest celowe — w tym zadaniu chodzi o to, żeby Jakub poćwiczył iterację (lekcja czwarta z pakietu).

## Materiały odniesienia

- [`biblioteka-rag/przewodnik-systemowy.md`](../biblioteka-rag/przewodnik-systemowy.md)
- [`biblioteka-rag/przyklady/`](../biblioteka-rag/przyklady/) — pięć wzorcowych komend Dawida (model do naśladowania)
- [`dla-pomocy-technicznej/04-lekcja-iteracja.md`](../dla-pomocy-technicznej/04-lekcja-iteracja.md) — jak rozmawiać z modelem, kiedy pierwsza odpowiedź nie jest doskonała
