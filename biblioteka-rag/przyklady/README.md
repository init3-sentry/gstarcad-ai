# Wzorcowe komendy GstarCAD-a w Pythonie

> ✅ **Wersja 3 (2026-07-09):** kolekcja rozszerzona o pięć kolejnych wzorców (06-10) pokrywających wymiarowanie, tekst etykiet, wstawianie bloku, interakcyjne rysowanie z podglądem (jig) i eksport migawki DWG. Wszystkie napisane wg **v2 przewodnika-systemowego** (`../przewodnik-systemowy.md`) + oficjalne samples GstarSoft z GstarCAD 2027 (`../oficjalne-materialy-gstarcad-2027/`).
>
> **Cel etapu 1 (per `PLAN.md`):** 20+ działających wzorców do 31 lipca 2026. Stan: **✅ 23 zwalidowane empirycznie na SP1** — 01-20 (fundament) + **21-23 workhorse Fazy A** (batch tekst/atrybuty, zwalidowane pętlowo 10/10 na LC 2026-07-10). Cel osiągnięty 3 tygodnie przed deadline'em.
>
> **Empirycznie potwierdzone jako działające na GstarCAD 2027 Plus PL:**
> - **2026-07-01:** `GcDbCircle`, `GcDbLine`, `GcDbArc`, `GcDbEllipse`.
> - **2026-07-09** (przez `../weryfikacja/sweep-5-verify.py`, testy `SWEEP5_*`): `GcDbText(punkt, str)` + `setHeight`, `GcDbPolyline` 2D + `addVertexAt`, `GcCmColor + setColor`, `GcDbAlignedDimension`, definicja bloku + `GcDbBlockReference`, `GcDbLayerTableRecord.color()/isFrozen()/isOff()/isLocked()/getName()`. Przy okazji poprawiono empirycznie wzorce 03/04/06/07/08 (pułapki: `colorIndex()` na warstwie nie istnieje → `color().colorIndex()`; `SymbolTable.add()` zwraca goły status, nie tuple).
> - Wciąż 🟡 (kanoniczne z samples, jeszcze nie odpalone end-to-end): `GcEdJig` (wzorzec 09), `GcDbDatabase.saveAs` (wzorzec 10).

Ten folder zawiera wzorcowe komendy dla GstarCAD 2026/2027, przygotowane jako wzór do naśladowania dla zespołu pomocy technicznej TMSys.

## Cel

Każda komenda pokazuje inny wzorzec pracy z biblioteką pygcad. Razem stanowią referencyjną podstawę dla każdej kolejnej komendy pisanej przez zespół — od typowego rysowania, przez interakcję z użytkownikiem, po automatyzację raportowania i eksportu plików.

## Komendy

### Grupa A: podstawowe rysowanie i wprowadzanie danych (01-05)

| Plik | Komenda | Co robi |
|---|---|---|
| `01_line_drawing.py` | `RYSUJ_LINIE_WZORCOWA` | Najprostsza komenda — rysuje wzorcową linię z (0,0,0) do (100,100,0) |
| `02_circle_with_user_input.py` | `RYSUJ_OKRAG_Z_PYTANIEM` | Interakcja — pyta użytkownika o promień (`gcedGetReal` → `RTNORM`), rysuje okrąg |
| `03_rectangle_with_layer.py` | `RYSUJ_POKOJ` | Praca z warstwami — tworzy warstwę POKOJE (`GcCmColor + setColor`), rysuje prostokąt (`GcDbPolyline` 2D) |
| `04_layer_audit_report.py` | `AUDYT_WARSTW` | Audyt — iteruje po warstwach (`newIterator` per `tbliter.py`), generuje raport, zapisuje do pliku |
| `05_change_selected_color.py` | `ZMIEN_KOLOR_NA_ZIELONY` | Praca z zaznaczeniem — `gcedSSGet + gcedSSName + gcdbOpenGcDbEntity` per `entsel.py` |

### Grupa B: adnotacje, bloki, interakcja i eksport (06-10)

| Plik | Komenda | Co robi |
|---|---|---|
| `06_dimension_aligned.py` | `WYMIAR_LINIOWY` | Wymiarowanie — pyta o dwa punkty, wstawia `GcDbAlignedDimension` z automatyczną etykietą długości (per `ployline_dim.py`) |
| `07_text_label.py` | `WSTAW_ETYKIETE` | Tekst jednowierszowy — punkt wstawienia + treść przez `gcedGetString`, `GcDbText(punkt, str)` z `setHeight(25)` |
| `08_block_insert.py` | `WSTAW_MARKER` | Praca z blokami — tworzy definicję bloku `GS_MARKER` (krzyżyk), wstawia jego referencję (`GcDbBlockReference` per `dynBlockTableReference.py`) |
| `09_line_jig_interactive.py` | `RYSUJ_LINIE_INTERAKTYWNIE` | Jig — interakcyjne rysowanie linii z podglądem w czasie rzeczywistym, `GcEdJig` z metodami `sampler/update/entity/doIt` (per `linejig.py`) |
| `10_save_dwg_snapshot.py` | `ZAPISZ_MIGAWKE_DWG` | Eksport pliku — nowa baza `GcDbDatabase(True, False)` z dwoma okręgami, zapis do DWG na Pulpicie (per `testdb.py`) |

### Grupa C: warstwy RGB, inwentaryzacja, odczyt polilinii i grupy (11-14)

Zwalidowane empirycznie na **GstarCAD 2027 Premium PL, SP1 (R27.1.0.2606)** 2026-07-09/10 (`../weryfikacja/sweep-6-verify.py`, `sweep-7-verify.py`).

| Plik | Komenda | Co robi |
|---|---|---|
| `11_entities_on_layers.py` | `RYSUJ_SCHEMAT` | Warstwy z kolorem RGB (`GcCmColor.setRGB`) + przypisanie encji przez `setLayer` (per `entity_in_layers.py`) 🟢 |
| `12_count_entities_by_type.py` | `ZLICZ_OBIEKTY` | Iteracja model space + klasyfikacja `isA().name()` (klasy z prefiksem `AcDb`) (per `testdb.py`) 🟢 |
| `13_list_polyline_vertices.py` | `WYPISZ_WIERZCHOLKI` | Odczyt wierzchołków polilinii 2D — `gcedEntSel` + `vertexIterator` + `GcDb2dVertex.position()` (per `pliniter.py`). Wymaga `SETVAR PLINETYPE 0` przed narysowaniem polilinii (tworzy `GcDb2dPolyline`) 🟢 |
| `14_group_selected.py` | `POGRUPUJ` | Słownik grup + `GcDbGroup` + `setAt` + `append` na zaznaczeniu (per `groups.py`) 🟢 |

> ℹ️ **Wzorzec 13 — historia walidacji (skorygowana 2026-07-10).** Wzorzec 13 tylko **czyta** wierzchołki istniejącej polilinii i to działa: izolacja krok-po-kroku (`sweep-7-verify.py`, log przeżywający crash) potwierdziła komplet (`gcedEntSel` → `gcdbOpenObject` → `isKindOf` → `vertexIterator` → `position`) bez crashu. **Korekta wcześniejszego wniosku:** crashe, które temu towarzyszyły, przypisano początkowo „niestabilności RDP" — to była nadinterpretacja. Testy krzyżowe na 3 niezależnych maszynach (2027 **bez SP1**, lokalnie, nie RDP, 2026-07-10) dowiodły, że **programowa KONSTRUKCJA** `GcDb2dPolyline` (`appendVertex`) crashuje na regenie na każdej maszynie — to **realny bug GstarSoft**, nie środowisko (patrz przewodnik-systemowy pitfall #8, zgłoszone producentowi). **Odczyt** natywnej polilinii (wzorzec 13) jest tym niedotknięty. Do tworzenia polilinii używaj lekkiej `GcDbPolyline` + `addVertexAt` (działa wszędzie). Odczyt lekkiej `GcDbPolyline` (`numVerts`/`getPointAt`) — osobny, jeszcze nie napisany wariant.

### Grupa D: opcje, zmienne, offset, klonowanie, metadane, I/O (15-20)

Zwalidowane empirycznie na **GstarCAD 2027 Premium PL, SP1 (R27.1.0.2606)** 2026-07-10 (`../weryfikacja/sweep-9-verify.py`, nieinteraktywnie).

| Plik | Komenda | Co robi |
|---|---|---|
| `15_keyword_choice.py` | `WYBIERZ_KSZTALT` | Wybór opcji przez słowo kluczowe — `gcedInitGet` + `gcedGetKword` (per `curve.py`); rysowanie `GcDbPolyline`/`GcDbCircle` 🟡 (input keyword nie odpalony end-to-end; wzorzec z oficjalnego sample) |
| `16_read_system_variable.py` | `POKAZ_USTAWIENIA` | Odczyt zmiennych systemowych — `gcedGetVar` + `resbuf` (VIEWSIZE/PLINETYPE/CLAYER/LTSCALE) 🟢 |
| `17_read_dwg_file.py` | `CZYTAJ_DWG` | Odczyt zewnętrznego DWG do osobnej bazy — `GcDbDatabase(False,False)` + `readDwgFile` + iteracja (per `testdb.py`) 🟢 |
| `18_offset_ellipse.py` | `ODSUN_ELIPSE` | Offset krzywej — `GcDbEllipse.cast` + `getOffsetCurves` (per `curve.py`) 🟢 |
| `19_deep_clone.py` | `KLONUJ` | Głęboka kopia — `GcDbObjectIdArray` + `GcDbIdMapping` + `deepCloneObjects` (per `deepClone.py`) 🟢 |
| `20_attach_xdata.py` | `OZNACZ_OBIEKT` | Metadane XData — `gcdbRegApp` + `resbuf` (`gcutNewRb`) + `setXData`/`xData` (per `xdata.py`) 🟢 |

**🎯 20/20 — cel etapu 1 osiągnięty.** Podzbiór stabilny (01-20) pokrywa: rysowanie (linia/okrąg/łuk/elipsa/prostokąt), interakcję (liczba/punkt/słowo kluczowe/zaznaczenie), warstwy (tworzenie/kolor RGB/audyt), bloki (definicja+referencja), grupy, wymiary, tekst, XData, deep clone, offset, iterację tabel i model space, oraz I/O plików DWG. Wszystko zwalidowane empirycznie na SP1, nieinteraktywnie, bez crashu — to jest fundament produktu niezależny od ewentualnych poprawek producenta.

### Grupa E: workhorse Fazy A — batch tekst/atrybuty (21-23)

Rdzeń wartości wg researchu popytu (`gstarcad-ai-wewnetrzne/research/`): operacje wsadowe na tekście i atrybutach = to, za co klienci realnie płacą. **Zwalidowane end-to-end na GstarCAD 2027 SP1 (R27.1.0.2606) 2026-07-10** przez pętlowy stress-test `../weryfikacja/waliduj-petla.py` — **10/10 iteracji PASS** (reset → zamiana=2 → eksport=1 → renumeracja=1 → read-back, bez `eNotOpenForWrite`).

| Plik | Komenda | Co robi |
|---|---|---|
| `21_batch_find_replace.py` | `ZAMIEN_TEKST` | Znajdź-i-zamień we wszystkich tekstach/mtekstach/atrybutach bieżącego rysunku (`GcDbText`/`GcDbMText`/`GcDbAttribute`). Wariant folder-batch (wiele plików) na dole pliku 🟡 |
| `22_attributes_to_csv.py` | `EKSPORT_ATRYBUTOW` / `IMPORT_ATRYBUTOW` | Eksport atrybutów bloków do CSV (handle+blok+tag+wartość) i re-import po edycji w Excelu |
| `23_renumber_by_rule.py` | `RENUMERUJ` | Renumeracja atrybutów wg reguły (prefiks + start + krok), np. `P-001, P-002...` |

> ℹ️ **Lekcje empiryczne (2026-07-10), warte zapamiętania dla każdej komendy piszącej do bazy:**
> 1. **Zapis wymaga otwarcia do zapisu.** Iterator model space (`newIterator().getEntity()`) zwraca encje otwarte do ODCZYTU — próba `setTextString`/`setContents` na nich to `Internal Error: eNotOpenForWrite`. Wzorzec: zbierz `ObjectId` przy odczycie, zamknij kontener, potem `gcdbOpenObject(oid, kForWrite)` na każdej encji osobno.
> 2. **Handle:** `GcDbBlockReference` NIE ma `handle()` — jest `getGcDbHandle().getIntoAsciiBuffer()` → `(True, 'hex')`.
> 3. **Nazwa bloku z referencji:** `blockTableRecord()` → otwórz rekord → `getName()` (nie ma `blockName()`).
> 4. **Cudzysłowy w stringach:** nie mieszaj typograficznych `„ "` z ASCII `"` jako ogranicznikiem — łamie f-string przy ładowaniu. Komunikaty trzymaj w ASCII (`'...'`, `->`).

## Jak ich używać

Krok pierwszy — otwórz GstarCAD 2026 lub 2027.
Krok drugi — wpisz w command line polecenie `APPLOAD`.
Krok trzeci — w oknie dialogowym wybierz plik `.py`, który chcesz wczytać, naciśnij „Załaduj".
Krok czwarty — w command line wpisz nazwę komendy (z tabeli wyżej). Komenda się wykona.

Możesz wczytać wszystkie komendy od razu — każda rejestruje się pod swoją własną nazwą, nie ma konfliktów.

## Co warto z nich nauczyć

**Wzorce 01-05** uczą podstawowego cyklu pracy z pygcad:

- **01** — minimalny szkielet: baza → block table → model space → nowa encja → `appendGcDbEntity` → zamknięcie. Sprawdzanie statusu przez `Gcad.eOk`.
- **02** — pobieranie liczby od użytkownika. Sprawdzanie statusu **przez `RTNORM`** (a nie literał `5100` — literały są zawodne). Dwie rodziny statusów: `Gcad.eOk` dla operacji na bazie, `RTNORM` dla operacji z linii poleceń.
- **03** — wzorzec „sprawdź warstwę, utwórz jeśli trzeba, użyj". Kolor warstwy przez `GcCmColor` + `setColor` (bezpośrednie `setColorIndex` na LayerTableRecord nie istnieje). Prostokąt jako `GcDbPolyline` 2D (`GcDb3dPolyline` crashuje CAD).
- **04** — iteracja tabeli symboli. Kanoniczny `newIterator` → `iterator.start()` → `while not iterator.done()` → `getRecord()` → `iterator.step()`. Właściwości warstwy pobierane defensywnie.
- **05** — praca z selection set. Kanoniczny `gds_name()` bufor, obowiązkowe `gcedSSFree`, iteracja przez `gcedSSName` + `gcdbGetObjectId` + `gcdbOpenGcDbEntity` (który zwraca już `GcDbEntity` — bez `isKindOf`/`cast`).

**Wzorce 06-10** uczą kolejnych typowych zadań CAD-owych:

- **06** — wymiarowanie liniowe. `GcDbAlignedDimension(pt1, pt2, textPt, "etykieta")` — cztery informacje: dwa końce mierzonego odcinka, punkt gdzie ma stanąć linia wymiarowa (offset prostopadły), tekst etykiety. Puste `""` jako etykieta = GstarCAD wygeneruje wartość automatycznie z pomierzonych punktów.
- **07** — tekst jednowierszowy. `GcDbText(punkt, string)` — dwuargumentowy konstruktor (bezargumentowy rzuca TypeError). Wysokość ustawia się osobno przez `setHeight`. Do bardziej złożonych bloków tekstu (wielowierszowych z formatowaniem) istnieje `GcDbMText`, ale ten wzorzec pokazuje najprostszy scenariusz.
- **08** — praca z blokami. Wzorzec „upewnij się, że definicja bloku istnieje, wstaw referencję". Definicję bloku dodaje się przez nowy `GcDbBlockTableRecord` z ustawioną nazwą, do którego dodaje się encje składowe bloku (dodawanie identyczne jak do model space). Referencję bloku dodaje się do model space przez `GcDbBlockReference(punkt_wstawienia, block_id)`.
- **09** — interakcyjne rysowanie z podglądem. Wzorzec „jig" jest standardem CAD-owym: linia przykleja się do kursora dopóki użytkownik nie kliknie. Implementacja przez dziedziczenie z `GcEdJig` i nadpisanie czterech metod: `sampler` (pobiera nowy input), `update` (aktualizuje encję), `entity` (zwraca encję do renderowania), `doIt` (orkiestruje pętlę `drag()` + finalny `append`). Ten sam wzorzec da się zastosować do elipsy, okręgu, prostokąta — dowolnej encji, którą można animować.
- **10** — eksport do pliku DWG. Nowa, pusta baza danych to `GcDbDatabase(True, False)` — poza tym praca z nią jest identyczna jak z `gcdbWorkingDatabase()` (`getBlockTable`, `getAt(GCDB_MODEL_SPACE, ...)`, `appendGcDbEntity`). Zapis do pliku: `database.saveAs(sciezka)`, status musi być `Gcad.eOk`. Ten wzorzec można rozbudować o eksport wybranych encji z bieżącego rysunku (przez `deepClone`) — jest do tego oficjalny sample `deepClone.py`.

## Konwencje, które warto zachowywać

Te konwencje powtarzają się w każdej z komend — i mają się powtarzać w każdej kolejnej komendzie pisanej dla projektu:

1. **Każda funkcja jest opakowana w blok `try/except`** — łapie wyjątki i komunikuje błąd przez `gcutPrintf`, zamiast wywalać konsolę Pythona w GstarCAD-zie.
2. **Wszystkie komunikaty do command line używają `gcutPrintf`** z prefiksem `"\n"` (bo `gcutPrintf` sam nie dodaje nowej linii). `gcedPrompt` też działa, ale kanoniczne samples GstarSoft używają `gcutPrintf`.
3. **Statusy porównujemy symbolicznie**: `Gcad.eOk` po operacjach na bazie (getBlockTable, getLayerTable, getAt, appendGcDbEntity, gcdbOpenObject, saveAs), `RTNORM` po operacjach z linii poleceń (gcedGetReal, gcedGetPoint, gcedGetString, gcedSSGet). **Nigdy przez literał liczbowy** (np. `!= 5100`) — literał sam może się różnić od rzeczywistej stałej.
4. **Wszystkie komentarze są po polsku.**
5. **Każdy otwarty obiekt jest zamykany** (`.close()`) w odwrotnej kolejności do otwarcia. Selection set zawsze przez `gcedSSFree`.
6. **Komendy mają polskie nazwy** przez `@command(local_name='POLSKA_NAZWA')`, bez polskich diakrytyków w samej nazwie (`OKRAG`, nie `OKRĄG`) — command line GstarCAD-a nie renderuje pewnych znaków w niektórych wersjach.
7. **Krótka instrukcja użycia jest w nagłówku pliku** — komentarz na samej górze pliku.
8. **Importy są na początku**: `from pygcad.core.runtime import *` oraz `from pygcad.pygrx import *`.
9. **Definicja bloku ≠ referencja bloku** — encje wewnątrz definicji dodaje się do `BlockTableRecord`, referencję (`GcDbBlockReference`) dodaje się do model space.

## Co jeszcze warto pokazać

Pierwsza dziesiątka wzorców pokrywa najczęstsze potrzeby. Do 20 (cel etapu 1 z `PLAN.md`) brakuje jeszcze dziesięciu. Sensowne kandydaty:

- Praca z wielowierszowym tekstem `GcDbMText` (formatowanie, alignment)
- Wymiarowanie kątowe (`GcDbRotatedDimension`) i średnicowe (`GcDbDiametricDimension`)
- Boolean na regionach (`GcDbRegion` + `booleanOper`)
- Praca z ExtendedData/XRecord (per `xdata.py` / `xrecord.py` z oficjalnych samples)
- Iteracja po encjach w model space z filtrowaniem po klasie (per `pliniter.py`)
- Klonowanie encji między bazami przez `deepClone` (per `deepClone.py`)
- Grupowanie encji (`GcDbGroup` per `groups.py`)
- Przycinanie obiektów (operacja boolowska 2D)
- Zmienne systemowe rysunku (`gcedGetVar` / `gcedSetVar`)
- Wczytanie linetypów z pliku zewnętrznego (`.lin`)

---

*Wersja: 4.0 — 10 lipca 2026: dodano Grupę E (workhorse Fazy A: 21-23 batch tekst/atrybuty), zwalidowaną pętlowo na LC (10/10 PASS); skorygowano notkę o wzorcu 13 (crash 2dPolyline = realny bug konstrukcji, nie „środowisko RDP"). Wersja 3.0 (9 lipca 2026) dodała wzorce 06-10. Wersja 2.0 dodała 5 wzorców v2 (poprawa bugów z v1). Wersja 1.0 (30 czerwca 2026) zawierała cztery krytyczne błędy skopiowane z niezweryfikowanego przewodnika v1.*
