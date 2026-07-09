# Wzorcowe komendy GstarCAD-a w Pythonie

> ✅ **Wersja 2 (2026-07-09):** wszystkie pięć wzorców zostało przepisanych na podstawie **v2 przewodnika-systemowego** (`../przewodnik-systemowy.md`), który sam wyrasta z (a) oficjalnych samples GstarSoft dla GstarCAD 2027 (`../oficjalne-materialy-gstarcad-2027/`) i (b) empirycznych testów pluginu ASKAI z 2026-07-01 na GstarCAD 2027 Plus PL. Wcześniejsza wersja (2026-06-30) zawierała cztery krytyczne błędy skopiowane z niezweryfikowanego przewodnika v1. Historia tych błędów oraz uzasadnienie każdej poprawki znajdują się w komentarzach nagłówkowych plików.
>
> **Empirycznie potwierdzone jako działające na GstarCAD 2027 Plus PL (2026-07-01):** `GcDbCircle`, `GcDbLine`, `GcDbArc`, `GcDbEllipse`. Wzorce dodatkowo używają `GcDbPolyline` (2D) oraz kanonicznych patternów z oficjalnych samples `tablerec.py` / `tbliter.py` / `entsel.py` — te patterny są 🟡 (dokumentowane przez GstarSoft), ale nie zweryfikowane end-to-end w tym repo.

Ten folder zawiera pięć wzorcowych komend dla GstarCAD 2026/2027, przygotowanych jako wzór do naśladowania dla zespołu pomocy technicznej TMSys.

## Cel

Każda z pięciu komend pokazuje inny wzorzec pracy z biblioteką pygcad. Razem stanowią one referencyjną podstawę dla każdej kolejnej komendy, którą zespół będzie pisał — od typowego rysowania, przez interakcję z użytkownikiem, po automatyzację raportowania.

## Komendy

| Plik | Komenda | Co robi |
|---|---|---|
| `01_line_drawing.py` | `RYSUJ_LINIE_WZORCOWA` | Najprostsza komenda — rysuje wzorcową linię z (0,0,0) do (100,100,0) |
| `02_circle_with_user_input.py` | `RYSUJ_OKRAG_Z_PYTANIEM` | Demonstruje interakcję — pyta użytkownika o promień, rysuje okrąg |
| `03_rectangle_with_layer.py` | `RYSUJ_POKOJ` | Praca z warstwami — tworzy warstwę POKOJE (kanoniczny `GcCmColor + setColor`) i rysuje na niej prostokąt (`GcDbPolyline` 2D) |
| `04_layer_audit_report.py` | `AUDYT_WARSTW` | Audyt — iteruje po warstwach (`newIterator` per `tbliter.py`), generuje raport, zapisuje do pliku |
| `05_change_selected_color.py` | `ZMIEN_KOLOR_NA_ZIELONY` | Praca z zaznaczeniem — `gcedSSGet + gcedSSName + gcdbOpenGcDbEntity` per `entsel.py` |

## Jak ich używać

Krok pierwszy — otwórz GstarCAD 2026 lub 2027.
Krok drugi — wpisz w command line polecenie `APPLOAD`.
Krok trzeci — w oknie dialogowym wybierz plik `.py`, który chcesz wczytać, naciśnij „Załaduj".
Krok czwarty — w command line wpisz nazwę komendy (z tabeli wyżej). Komenda się wykona.

Możesz wczytać wszystkie pięć komend od razu — każda rejestruje się pod swoją własną nazwą, nie ma konfliktów.

## Co warto z nich nauczyć

**Pierwsza komenda** uczy minimalnego cyklu: otwarcie bazy → dostęp do model space → utworzenie obiektu → dodanie do bazy → zamknięcie wszystkiego → komunikat. Każda następna komenda zawiera ten sam szkielet, tylko z dodatkowymi elementami. Zwróć uwagę na sprawdzanie statusu przez `Gcad.eOk` po każdym otwarciu tabeli i po `appendGcDbEntity`.

**Druga komenda** uczy interakcji z użytkownikiem przez `gcedGetReal`. Zwróć uwagę na sprawdzanie statusu przez **`RTNORM`** (a nie przez literał `5100`, jak było w v1 wzorca — literał daje w istocie ZAWSZE odrzucenie danych, ponieważ prawdziwy `RTNORM` ma inną wartość). Rodziny statusów są dwie: `Gcad.eOk` dla operacji na bazie, `RTNORM` dla operacji z linii poleceń (input użytkownika, selection set).

**Trzecia komenda** uczy pracy z tabelą warstw. Wzorzec „sprawdź czy warstwa istnieje, utwórz jeśli nie, użyj" jest jednym z najczęściej powtarzanych w skryptach CAD-owych. **Kolor warstwy** ustawiamy przez obiekt `GcCmColor` (`color.setColorIndex(n)` + `record.setColor(color)`) — bezpośrednio na `GcDbLayerTableRecord` nie ma metody `setColorIndex`. Do rysowania prostokąta używamy **`GcDbPolyline` 2D** z `addVertexAt`, zamykamy przez powrót do punktu startowego — `GcDb3dPolyline + setClosed` empirycznie crashuje GstarCAD-a do desktopu.

**Czwarta komenda** uczy iteracji po tabelach symboli — tu warstw, ale ten sam wzorzec stosuje się dla bloków, stylów tekstu, stylów wymiarowania. Wzorzec jest kanoniczny — dokładnie taki jak w oficjalnym `tbliter.py`: `newIterator` → `iterator.start()` → `while not iterator.done()` → `getRecord()` bez argumentu → `iterator.step()`. Właściwości warstwy (`colorIndex`, `isFrozen`, `isOff`, `isLocked`) pobieramy defensywnie, bo nie wszystkie są jeszcze empirycznie zweryfikowane na tej wersji API.

**Piąta komenda** uczy pracy z zaznaczeniem użytkownika wg kanonicznego `entsel.py`: selection set trzymamy w `gds_name()`, iterujemy przez `gcedSSName` + `gcdbGetObjectId` + `gcdbOpenGcDbEntity` (który zwraca już `GcDbEntity` — bez potrzeby `isKindOf` / `cast`). Selection set **zawsze zwalniamy** przez `gcedSSFree(sset)` na końcu.

## Konwencje, które warto zachowywać

Te konwencje powtarzają się w każdej z pięciu komend — i mają się powtarzać w każdej kolejnej komendzie pisanej dla projektu:

1. **Każda funkcja jest opakowana w blok `try/except`** — łapie wyjątki i komunikuje błąd przez `gcutPrintf`, zamiast wywalać konsolę Pythona w GstarCAD-zie.
2. **Wszystkie komunikaty do command line używają `gcutPrintf`** z prefiksem `"\n"` (bo `gcutPrintf` sam nie dodaje nowej linii). `gcedPrompt` też działa, ale kanoniczne samples GstarSoft używają `gcutPrintf`.
3. **Statusy porównujemy symbolicznie**: `Gcad.eOk` po operacjach na bazie (getBlockTable, getLayerTable, getAt, appendGcDbEntity, gcdbOpenObject), `RTNORM` po operacjach z linii poleceń (gcedGetReal, gcedGetPoint, gcedSSGet). **Nigdy przez literał liczbowy** (np. `!= 5100`) — literał sam może się różnić od rzeczywistej stałej.
4. **Wszystkie komentarze są po polsku.**
5. **Każdy otwarty obiekt jest zamykany** (`.close()`) w odwrotnej kolejności do otwarcia. Selection set zawsze przez `gcedSSFree`.
6. **Komendy mają polskie nazwy** przez `@command(local_name='POLSKA_NAZWA')`, bez polskich diakrytyków w samej nazwie (`OKRAG`, nie `OKRĄG`) — command line GstarCAD-a nie renderuje pewnych znaków w niektórych wersjach.
7. **Krótka instrukcja użycia jest w nagłówku pliku** — komentarz na samej górze pliku.
8. **Importy są na początku**: `from pygcad.core.runtime import *` oraz `from pygcad.pygrx import *` (obie te przestrzenie są potrzebne, obie są małe i przewidywalne — wildcard OK).

## Co jeszcze warto pokazać

Te pięć wzorców pokrywa najpopularniejsze potrzeby. Z czasem warto rozszerzyć kolekcję o:

- komendę z wymiarowaniem (`GcDbAlignedDimension` — jest oficjalny sample `ployline_dim.py`)
- komendę z tekstem wielowierszowym (`GcDbMText`)
- komendę z blokiem (wstawianie z biblioteki bloków)
- komendę przycinającą obiekty (operacja boolowska)
- komendę z jig'iem (rysowanie interaktywne z podglądem — jest oficjalny sample `linejig.py`)

Te rozszerzenia trafią do folderu `przyklady/` w miarę powstawania (w etapie trzecim projektu — galeria mistrzowska).

---

*Wersja: 2.0 — 9 lipca 2026. Poprzednia wersja 1.0 (30 czerwca 2026) zawierała cztery krytyczne błędy skopiowane z niezweryfikowanego przewodnika v1 — przepisane wg empirycznie ugruntowanego przewodnika v2.*
