# T-006 — Pierwsza własna komenda: AUDYT_WARSTW_DO_PLIKU (Tomasz Gach)

| Pole | Wartość |
|---|---|
| Identyfikator | T-006 |
| Etap | pierwszy |
| Przypisany do | **Tomasz Gach** |
| Przewidywany czas | 8 godzin |
| Status | oczekuje |
| Data wejścia | 2026-07-15 |
| Data deklarowanego ukończenia | 2026-07-25 |
| Zależy od | T-002 (Tomasz przeszedł wprowadzenie plus zweryfikował wzorcowe komendy) |

## Cel

Napisanie własnej komendy **AUDYT_WARSTW_DO_PLIKU**, która generuje raport tekstowy listujący wszystkie warstwy bieżącego rysunku z informacją o liczbie obiektów na każdej warstwie, kolorze, typie linii i grubości. Raport jest zapisywany do pliku tekstowego o nazwie zgodnej z nazwą rysunku, w tym samym folderze.

## Kryteria akceptacji

- [ ] Plik `przyklady-chlopcow/tomasz/audyt_warstw_do_pliku.py` istnieje w gałęzi roboczej
- [ ] Komenda zarejestrowana jako `AUDYT_WARSTW_DO_PLIKU` po załadowaniu poleceniem `APPLOAD`
- [ ] Wygenerowany raport ma czytelną strukturę (tabela lub listy) i zawiera co najmniej: nazwa warstwy, kolor, typ linii, grubość linii, liczba obiektów
- [ ] Komenda działa na rysunku testowym dostarczonym przez Dawida
- [ ] Plik `README.md` z opisem komendy w polskim
- [ ] Dwa zrzuty ekranu pokazujące działanie i przykładowy raport

## Wskazówki techniczne

Główne elementy pygcad, które tu wykorzystasz:

- `GcDbLayerTable` plus `GcDbLayerTableRecord` — iteracja po warstwach i odczyt ich właściwości (kolor, typ linii, grubość)
- `GcDbBlockTable` plus `GcDbBlockTableRecord` (model space) — iteracja po obiektach rysunku, każdy obiekt ma metodę `layer()` zwracającą nazwę warstwy
- standardowa biblioteka Pythona do zapisu pliku tekstowego (`open(path, 'w', encoding='utf-8')`)

## Materiały odniesienia

Te same co T-005.
