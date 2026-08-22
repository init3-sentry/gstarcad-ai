# Katalog narzędzi — co mamy, co działa, skąd pobrać

> _Stan na 2026-08-21._ **To jest jedyny obowiązujący katalog narzędzi.** Wszystkie repozytoria projektu linkują tutaj. Zmiana statusu, nazwy komendy albo nowe narzędzie — **zmienia się tylko ten plik**.
>
> Jak uruchomić którekolwiek z nich: **[JAK-URUCHOMIC.md](JAK-URUCHOMIC.md)**.
>
> **Aktualizacja 2026-08-06:** dystrybucja przeszła na **instalator self-service** (`instalator-gsai` w *powertools*) — klient uruchamia jeden plik, który dokłada Python + skrypty do GstarCAD, bez ręcznego „Download raw file". Instalator testowany przez zespół na czystych maszynach ([zespol#78](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/78)): przechodzi; jeden edge-case (Python już all-users) naprawiony, retest w toku. Runda testów serii generatywnej v2 po werdyktach Roberta: [zespol#79](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/79).

---

> ### 📣 Aktualizacja 2026-08-15 — dla marketingu (strona)
>
> Zmiany z pełnego przeglądu Roberta 14–15.08. Skrót do przeniesienia na stronę:
>
> **⛔ Wyleciało — usunąć ze strony:**
> - `GSAI_ZESTAWIENIE` i `GSAI_PRZEDMIAR` → **wchłonięte przez `GSAI_POLA`** (jedno narzędzie: pole + obwód + opis + tabela + eksport CSV). Robert potwierdził konsolidację.
> - `GSAI_KOLEJNOSC` (kolejność rysowania warstw) → GstarCAD ma to natywnie i lepiej (`DRAWORDER`, opcja nad/pod obiekt). Robert: „zamykamy temat". Usunięte.
>
> **➕ Doszło — nowe narzędzia (kandydaci premierowi, w teście zespołu; na stronę PO odbiorze praktyka):**
> - **`GSAI_ZNAKI`** — tarcze znaków drogowych pionowych (grupy A/B/C/D) + znak B-33 wg Dz.U. 2003/2181, wynik jako blok.
> - **`GSAI_PRZEJEZDNOSC`** — analiza przejezdności (swept-path): obwiednia pojazdu miarodajnego na trasie + ścięcie zakrętu (śmieciarka, naczepa, autobus…).
> - **`GSAI_AKUSTYKA`** — kalkulator czasu pogłosu RT60 + ocena zgodności z PN-B-02151-4, tabela wyników na rysunku.
> - **`GSAI_MEBLE`** — rozbudowany katalog ~60 symboli (kuchnia, sanitariat, meble pokojowe) wstawianych jako bloki (poprzednia wersja była szczątkowa).
>
> **🔄 Zmieniło funkcję — nowy opis na stronę:**
> - **`GSAI_POLA`** — łączy pole i obwód pól/pomieszczeń; opis w pomieszczeniu do wyboru (numer / powierzchnia / oba), tabela zbiorcza, eksport CSV/przedmiar.
> - **`GSAI_POMIAR`** — dokłada typ pomiaru w opisie (obwód dla zamkniętych) + przerywaną linię skąd-dokąd.
> - **`GSAI_ZLICZ`** — radzi sobie z blokami dynamicznymi (liczy po nazwie efektywnej, nie po anonimowej `*U###`).
> - **`GSAI_LINIA`** — wyśrodkowany opis w przerwie linii + wybór czcionki / dowolnego znaku (z ostrzeżeniem o przenośności).
> - **`GSAI_SCHODY`** — opis czyta się wzdłuż biegu, pełna strzałka na łuku, czerwone podświetlenie wartości niezgodnych z normą.
>
> Uwaga dla strony: pozycje z „doszło" i część „zmieniło" czekają na runtime-test zespołu/Roberta. **Publiczny opis dopiero po odbiorze praktyka** — do tego czasu trzymamy je jako „wkrótce / w testach", nie jako gotowe.

**Komendy mają przedrostek `GSAI_`** (zmiana z 14.07.2026). Wpisuje się np. `GSAI_IMPORTXYZ`. Stare nazwy bez przedrostka już nie działają — po pobraniu nowej wersji trzeba zrobić `APPLOAD` jeszcze raz.

**Jak pobrać:** kliknąć nazwę pliku → na stronie pliku przycisk **„Download raw file"** (prawy górny róg). Pilnować, żeby zapisało się jako `.py`, nie `.txt`. Wszystko naraz: zielony **Code → Download ZIP**.

---

## ✅ Działają — zwalidowane na prawdziwych rysunkach (kandydaci na premierę)

Sprawdzone na prawdziwych rysunkach projektowych — tych ciężkich, z bałaganem po poprzednim projektancie. **To najlepsze źródło problemów, jakie mamy** — narzędzie, które działa tylko na sztucznie wygenerowanym pliku, jest do niczego.

| Komenda | Co robi | Plik | Zwalidował |
|---|---|---|---|
| **`GSAI_RENAME_WARSTWY`** 🦸 | Hurtowa zmiana nazw warstw wzorcem (find→replace w środku nazwy) z obsługą kolizji. Natywnie GstarCAD tego nie ma — **lukę potwierdził na piśmie QA Manager Autodesku** (ADR 08). Wartość = hurt/wzorzec, nie pojedyncza warstwa. | źródło [31_rename_warstw_wzorcem.py](biblioteka-rag/przyklady/31_rename_warstw_wzorcem.py) → **doportowane do instalatora 2026-08-12** (`skrypty/GSAI_RENAME_WARSTWY.py`, AST+stuby 🟢) | Tomasz 29.07 (hurt); **re-test w instalce przed premierą** |
| **`GSAI_IMPORTXYZ`** | Plik z Excela/Notatnika ze współrzędnymi → punkty z numerami. Natywnie brak (płatne nakładki = dowód popytu). | źródło [25_import_coordinates.py](biblioteka-rag/przyklady/25_import_coordinates.py) → **doportowane do instalatora 2026-08-12** (`skrypty/GSAI_IMPORTXYZ.py`, AST+stuby 🟢) | Robert; **re-test w instalce przed premierą** |
| **`GSAI_AUDYTZ`** | Znajduje i zaznacza obiekty, które „uciekły" w Z≠0 (z góry niewidoczne, psują pomiary w płaskim rysunku). Prostowanie natywnym `FLATTEN`. | źródło [26_audit_z_axis.py](biblioteka-rag/przyklady/26_audit_z_axis.py) → **doportowane do instalatora 2026-08-12** (`skrypty/GSAI_AUDYTZ.py`, AST+stuby 🟢) | Jakub 29.07; **re-test w instalce przed premierą** |
| **`GSAI_SCHODY`** 🎁 | Generator schodów (rzut / łuk / przekrój; tryby biegu) — „wow": schody w GstarCAD za darmo. **Rysuje też po ponownym otwarciu pliku** (generatywne → odporne na BUG-10). | kod w repo *powertools*, dostawa: release `skrypty-test` | Tomasz 31.07; **v2 06.08** (cm zamiast mm, wynik jako blok, auto-opis); **v3 15.08 po robert#16**: opis czyta się wzdłuż biegu, pełna strzałka na łuku (Robert ✓), czerwone podświetlenie niezgodności z normą. Zostaje od Roberta: „typ opisów wg normy" + opcja opisów jako atrybuty. |
| **`GSAI_STRZALKA_POLNOCY`** 🧭 | Ozdobna strzałka północy — **6 stylów dwutonowych** (prosta/strzałka/romb/róża wiatrów/kompas geodezyjny/iglica), panel wyboru z podglądem + wysokość + klik. **v2 06.08: wynik jako blok na bieżącej warstwie** (obrót przez ROTATE, przesuń/kasuj jako jeden obiekt). Natywnie brak (GstarCAD ma tylko `COMPASS`/`NORTHDIRECTION`). Generatywne → BUG-10-safe. `GSAI_STRZALKA_GALERIA` = wszystkie naraz. | kod w *powertools*, release `skrypty-test` | LC 01.08 → **zespół 06.08 (Tomasz ✓, [#79](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/79))** |
| **`GSAI_SLONCE`** ☀️ | Diagram nasłonecznienia / ścieżka słońca (biegunowy wykres): szerokość geo + data → horyzont, pierścienie wysokości, azymuty N/E/S/W, ścieżka słońca + przesilenia/równonoc. Okno z **dropdownem 18 miast wojewódzkich** + ręczna szerokość. **v2 06.08: legenda „jak czytać"** (praktyk brał to za mapę cienia). Generatywne → BUG-10-safe. Spina z **Linijką Słońca**. `GSAI_SUNPATH` = alias. | kod w *powertools*, release `skrypty-test` | LC 02.08 → **zespół 06.08 (Tomasz ✓, [#79](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/79))** |
| **`GSAI_SPADEK`** 📐 | Strzałka spadku + wartość (%/‰/°/1:n) — dachy, tarasy, odwodnienie; tryb ręczny albo auto z różnicy wysokości. Natywnie brak. Generatywne → BUG-10-safe. | kod w *powertools*, release `skrypty-test` | **runtime ✓ Jakub 06.08** (oba tryby, V2607); ocena praktyczna Roberta [robert#9](https://github.com/init3-sentry/gstarcad-ai-robert/issues/9) w toku |
| **`GSAI_POLA`** 🎁 | Pole i obwód pól/pomieszczeń: zaznacz oknem albo wskaż pomieszczenie → opis w centroidzie + tabela zbiorcza + eksport CSV. Liczy też na **pliku ZAPISANYM od klienta** (ścieżka COM, obejście BUG-10). Wchłonęło ZESTAWIENIE i PRZEDMIAR (konsolidacja, Robert ✓). | kod w *powertools*, release `skrypty-test` | **zespół 17.08 ([#102](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/102)), plik zapisany, V2607: Jakub ✓ + Tomasz ✓** (po fixach SUMA/CSV/jednostki) |
| **`GSAI_POMIAR`** | Pomiar z opisem: długości + odległość punkt-punkt, „obwód" w opisie zamkniętej polilinii, linia przerywana skąd-dokąd, przełącznik orientacji opisu. Natywnie brak takiego złożenia. | kod w *powertools*, release `skrypty-test` | **Jakub ✓ 17.08 ([#102](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/102), V2607)** |
| **`GSAI_ZLICZ`** | Zliczanie obiektów wg kryterium (warstwa/blok/typ) → tabela na rysunku; **bloki dynamiczne liczone po nazwie efektywnej** (nie po anonimowej `*U###`). | kod w *powertools*, release `skrypty-test` | **Jakub ✓ 17.08 ([#102](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/102), V2607)** |
| **`GSAI_LINIA`** | Generator złożonego rodzaju linii z wtopionym tekstem (`—A—A—`); opis wyśrodkowany w przerwie + wybór stylu tekstu. Natywnie brak. Generatywne → BUG-10-safe. | kod w *powertools*, release `skrypty-test` | **Jakub ✓ 17.08 ([#102](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/102), V2607)** (po poprawce etykiety „styl tekstu") |

> **Bramka przed premierą (nie pomijać):** te narzędzia zespół ma jeszcze przejść **na pliku ZAPISANYM → otwartym ponownie** (bo BUG-10 — patrz niżej — ujawnił różnicę „świeży rysunek" vs „plik klienta"). RENAME/IMPORTXYZ/AUDYTZ/SCHODY są konstrukcyjnie BUG-10-safe, ale gate potwierdza to na realnym workflow.

## 🟡 Warunkowe / w testach

| Komenda | Co robi | Plik | Stan |
|---|---|---|---|
| ~~**`GSAI_PRZEDMIAR`**~~ | Pole + obwód wskazanych obiektów → CSV (Excel). | — | ⛔ **Wycofane 2026-08-15 — wchłonięte przez `GSAI_POLA`** (eksport CSV/przedmiar jest teraz opcją w POLA). Robert potwierdził konsolidację. |
| **`GSAI_DLUGOSC`** / **`GSAI_DLUGOSC_OPIS`** | Suma długości; `_OPIS` dokłada etykietę na rysunku. | [GSAI_DLUGOSC.py](biblioteka-rag/przyklady/GSAI_DLUGOSC.py) · [29_dlugosc_opis.py](biblioteka-rag/przyklady/29_dlugosc_opis.py) | Zwalidowane na **ŚWIEŻYM** rysunku (Jakub 29.07), ale 🔴 **BUG-10 na zapisanych** (`length` pada). Do przepisania na `entget` albo fix R&D. |
| **`GSAI_FORMATKA`** 📐 | **07.08 ROZDZIELONE wg werdyktu Roberta ([robert#9](https://github.com/init3-sentry/gstarcad-ai-robert/issues/9), mail 2026-08-05 + wzorzec `formatka-uniwersalna-robert.dwg`).** Teraz: SAMA ramka **ISO 5457** (margines 20mm lewy / 10mm pozostałe — zweryfikowane w normie), formaty A4/A3/A2 (A4 też poziomo), guard „tylko Arkusz", **BEZ tabliczki** (każda firma ma własną). Natywnie brak w bazie Professional (Mechanical ma). Generatywne → BUG-10-safe. | kod w *powertools*, release `skrypty-test` | 🟡 **Do retestu zespołu** po rozdziale — poprzednia wersja (rama+tabliczka razem) była na LC (Dawid 02.08); nowy podział jeszcze nie testowany na LC/zespole. ⚠️ testerzy: klawiatura **Polski (Programisty)**, nie 214. |
| **`GSAI_TABELKA`** 📐 | **NOWA 07.08** — połowa rozdziału `GSAI_FORMATKA`: tabliczka rysunkowa **ISO 7200** (PL) + pas właściciela (logo + Biuro) jako osobny blok **ATTDEF**, dla tych bez własnej tabliczki. Szerokość **180 mm** (≤180mm, wymóg Roberta), wysokość 57mm. **Punkt wstawienia = prawy dolny narożnik** (klik, tabliczka rozwija się w lewo/górę — dosuwalna do dowolnego rogu ramki). Guard „tylko Arkusz". Generatywne → BUG-10-safe. Styl **TTF `GSAI_PL`** dla polskich znaków. | kod w *powertools*, release `skrypty-test` | 🟡 **Nowe, nie testowane** — walidator AST 🟢 OK, brak jeszcze przebiegu na LC/zespole. |
| **`GSAI_WEKTORYZUJ`** *(prototyp)* | Skan rastrowy → polilinie, lokalnie. | [wektoryzacja.py](biblioteka-rag/przyklady/wektoryzacja.py) | Prototyp; oddzielanie tekstu do walidacji u Jakuba. OCR = v2.0 (ADR 05). |
| **`GSAI_CHROPOWATOSC`** | Symbol chropowatości powierzchni (haczyk 60°, warianty usunięcia materiału, półka na dane). | źródło [27_surface_roughness.py](biblioteka-rag/przyklady/27_surface_roughness.py) → **doportowane do instalatora 2026-08-12** (`skrypty/GSAI_CHROPOWATOSC.py`, AST+stuby 🟢) | 🟡 **Do testów zespołu ([zespol#67](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/67))** — norma potwierdzona (**PN-EN ISO 21920-1:2022** zastąpiła ISO 1302; symbol przeniesiony bez zmian, wartość=wolny tekst). Czeka wizualny werdykt Roberta. Generatywne → BUG-10-safe. |
| **`GSAI_WARSTWY_STANDARD`** | Tworzy polski standard warstw (branże A/K/instalacje/Z + systemowe, ~165 warstw) jednym poleceniem, panel wyboru branż. Natywnie brak. Generatywne → BUG-10-safe. | kod w *powertools* | 🟡 **v2 06.08** po uwagach Roberta ([robert#13](https://github.com/init3-sentry/gstarcad-ai-robert/issues/13)): rodziny kolorów RGB, rozbite instalacje, grubości per warstwa. Czeka akcept Roberta + test v2 na Windows. |
| **`GSAI_SYMBOL_RZUTOWANIA`** | Tabliczkowy symbol metody rzutowania 1./3. kąta (ISO 5456-2) — ścięty stożek w dwóch widokach. Natywnie brak. Generatywne. | kod w *powertools* | 🟡 **06.08 przemianowane z `GSAI_RZUTOWANIE`** (stara nazwa myliła — Robert robert#9). Do testu. |
| **`GSAI_RZEDNE`** | Znacznik rzędnej wysokościowej na przekroju/rzucie — wskaż punkt bazowy ±0,000 (DOWOLNY, nie początek układu), potem kolejne punkty; auto-odczyt Y liczy różnicę. Grot otwarty/zamknięty-w-połowie-czarny wg PN-B-01025:2004 §3.5, każdy znacznik = BLOK. Natywnie brak dedykowanego. Generatywne. | kod w *powertools* | 🟡 **v2 07.08 po robert#1** (Robert przesłał skany strony normy + poprosił wprost o znacznik na przekroju liczony od wskazanego punktu). Naprawione: format liczby kropka→przecinek, domyślna skala 1.0→cm (100), kształt grota wg skanów (otwarty/zamknięty-w-połowie zamiast błędnej chorągiewki), grupowanie w blok. **Kształt symbolu do pokazania Robertowi przed testem zespołu — nie był z nim jeszcze zweryfikowany wizualnie.** AST/pygcad walidator zielony, NIE testowane na LC/Windows. |
| **`GSAI_NUMERACJA`** | Automatyczne wstawianie i inkrementacja numerów rysunków/arkuszy. | kod w *powertools* | 🟡 zbudowane; **status testu do potwierdzenia**. |
| **`GSAI_CUI`** | „Odzyskaj wstążkę" — naprawa interfejsu GstarCAD po uszkodzonym `gcad.cuix` / porwanym rejestrze `MenuFile` (znika wstążka/menu). Przywraca z baseline sprzed instalacji albo z 5 zdrowych snapshotów (ring), naprawia rejestrację głównego menu; okno z przyciskiem „Odzyskaj wstążkę" + modal „ZRESTARTUJ GstarCAD". Naprawa interfejsu, nie danych — rysunki nietknięte. Alias globalny: GSAI_REPAIRCUI. | kod w *powertools* (`skrypty/GSAI_CUI.py` + `gsai_cui_core.py`, integracja `GSAI_AUTOSTART.py`; self-test core 16/16) | 🟡 zbudowane + **zwalidowane e2e na LC 22.08** (repro: hijack `MenuFile` → restore → wstążka wraca) + **na produkcji** (release `2026.08.22-cbaf250`, bundle `cbaf2503f2cb`, auto-load bez APPLOAD). Publiczny opis na stronę **czeka na odbiór Roberta**. |
| **`GSAI_LEGENDA_WARSTW`** | Wstawia legendę warstw jako tabelę na rysunku: nazwa + próbka koloru + próbka typu linii (graficznie) + szerokość + druk + opis. Pomysł Roberta ([robert#13](https://github.com/init3-sentry/gstarcad-ai-robert/issues/13)). Natywnie brak. Generatywne → BUG-10-safe. | kod w *powertools* (`skrypty/GSAI_LEGENDA_WARSTW.py` + `gsai_legenda_core.py`, self-test 11/11) | 🟡 zbudowane; **w testach zespołu, na stronę po odbiorze praktyka**. |
| **`GSAI_ZNAKI`** | Tarcze pionowych znaków drogowych (grupy A/B/C/D) + znak B-33 wg Dz.U. 2003/2181; wynik jako blok. | kod w *powertools* | 🟡 **w testach zespołu, na stronę po odbiorze praktyka** (kandydat premierowy 15.08). |
| **`GSAI_PRZEJEZDNOSC`** | Analiza przejezdności (swept-path): obwiednia pojazdu miarodajnego na trasie + ścięcie zakrętu (śmieciarka, naczepa, autobus). | kod w *powertools* | 🟡 **w testach zespołu, na stronę po odbiorze praktyka** (kandydat premierowy 15.08). |
| **`GSAI_AKUSTYKA`** | Kalkulator czasu pogłosu RT60 + ocena zgodności z PN-B-02151-4; tabela wyników na rysunku. | kod w *powertools* | 🟡 **w testach zespołu, na stronę po odbiorze praktyka** (kandydat premierowy 15.08). |
| **`GSAI_MEBLE`** | Rozbudowany katalog ~60 symboli (kuchnia, sanitariat, meble pokojowe) wstawianych jako bloki. | kod w *powertools* | 🟡 **w testach zespołu, na stronę po odbiorze praktyka** (kandydat premierowy 15.08). |
| **Linie urbanistyczne** (`planninglines`) | 42 znormalizowane wzory: linia zabudowy obow./nieprzekraczalna, tory, ogrodzenie, skarpa, granice, rozbiórka. Od Roberta ([robert#10](https://github.com/init3-sentry/gstarcad-ai-robert/issues/10)). | `powertools/04-gsai-linie/robert-planninglines/` | 🟡 wciągnięte 06.08. **Wymaga `RODZLIN.shx` w Fontach GstarCAD** (instalator musi dowozić) — inaczej linie stają się ciągłe. Do testu ładowania + skali. |
| **`GSAI_ORNAMENT`** | Demonstracyjny generator wzorów geometrycznych (algorytm, nie AI). | kod w *powertools* | ⛔ **DO WYWALENIA 06.08 — Robert kazał usunąć** ([robert#9](https://github.com/init3-sentry/gstarcad-ai-robert/issues/9): brak zastosowania). Poza ofertą i poza stroną. |

> ### 🆕 Aktualizacja 2026-08-21 — Suite GEO (Geoportal) + moduł OC (schron), w runtime-teście zespołu
>
> Dwa nowe zestawy weszły w **runtime-test zespołu, przed odbiorem praktyka (Robert)** — publiczny opis dopiero po jego werdykcie. Oznaczenie modelu opłat: **🆓 darmowe** (podkład + pojedyncza działka) / **💰 płatne** (moduł/analiza), wg decyzji Dawida z 2026-08-21 (geoportal = freemium; schron = płatny moduł OC).

**Suite GEO (Geoportal)** — bundle `GSAI-geoportal-test.zip` na release `skrypty-test` w [`gstarcad-ai-zespol`](https://github.com/init3-sentry/gstarcad-ai-zespol), SHA256 `d083599cac41382f33da9238c09adf2ff6f7e6dfbb22320ccd8f6b0ab0b78783`, zgłoszenie [zespol#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113). Źródła w `narzedzia-do-testow/`: `geoportal.py` + `gsai_wladanie.py` + `gsai_pog.py` + `gsai_zabytki.py` + `gsai_geologia.py`. **Dane GUGiK / NID / PIG są bezpłatne** (art. 40a Prawa geodezyjnego i kartograficznego) — nasza wartość to integracja wprost w GstarCAD, nie sprzedaż danych. Graduacja pozycji „Dane z Geoportalu" z sekcji *W budowie*.

| Komenda | Co robi | Plik | Stan |
|---|---|---|---|
| **`GSAI_DZIALKI`** 🆓 | Wskaż punkt → obrys działki + numer + powierzchnia (ULDK/EGiB). Podkład. | bundle `GSAI-geoportal-test.zip` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_BUDYNKI`** 🆓 | Obrysy budynków w okolicy wskazanego punktu (EGiB/BDOT10k). | bundle `GSAI-geoportal-test.zip` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_WYSOKOSC`** 🆓 | Etykieta wysokości H z Numerycznego Modelu Terenu (GUGiK). | bundle `GSAI-geoportal-test.zip` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_ORTOFOTO`** 🆓 | Podkład ortofotomapy jako raster (PZGIK/GUGiK). | bundle `GSAI-geoportal-test.zip` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_GEOPORTAL`** 🆓 | Panel checkboxów: wskaż punkt → zaciąga zaznaczone warstwy. Agregator pozostałych narzędzi geo. | bundle `GSAI-geoportal-test.zip` · `geoportal.py` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_WLADANIE`** 🆓 | Wskaż punkt → kto włada działką (Skarb Państwa / gmina / osoba fizyczna — **bez nazwisk, RODO**) + ścieżka „do kogo się zwrócić". Źródło: KIEG (`grupa_rejestrowa`). Podstawa: §14 rozp. EGiB (Dz.U. 2024/219). Hak — pojedyncza działka. | bundle `GSAI-geoportal-test.zip` · `gsai_wladanie.py` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_TRASA`** 💰 | Wskaż polilinię przyłącza → wykaz przeciętych działek (obrysy + numery) w rysunku. | bundle `GSAI-geoportal-test.zip` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_WYKAZ`** 💰 | Wskazana działka + sąsiedzi graniczni → tabela właścicieli/instytucji na rysunku. | bundle `GSAI-geoportal-test.zip` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_POG`** 💰 | Plan Ogólny gminy: strefa planistyczna + wskaźniki (maks. intensywność, maks. % zabudowy, maks. wysokość, min. pow. biologicznie czynna) + flaga Obszaru Uzupełnienia Zabudowy + policzona koperta chłonności z pola działki. Źródło: usługa `PlanyOgolneGmin` (WMS). Podstawa: reforma planistyczna (ust. 7.07.2023) + rozp. MRiT 8.12.2023 + WT §39 (Dz.U. 2022/1225). ⚠️ Mało gmin ma uchwalony POG (Studia obowiązują do 31.08.2026) — „brak POG" to **poprawny wynik**. Spina dawne narzędzia chłonność + POG. | bundle `GSAI-geoportal-test.zip` · `gsai_pog.py` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_ZABYTKI`** 💰 | Wskaż punkt → czy objęty ochroną konserwatorską (NID: zabytek nieruchomy / archeologiczny / UNESCO) + numer rejestru + „wymagane pozwolenie WKZ". Źródło: usługi INSPIRE NID (`usluga.zabytek.gov.pl`). Podstawa: art. 36 ust. z 23.07.2003 o ochronie zabytków. | bundle `GSAI-geoportal-test.zip` · `gsai_zabytki.py` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |
| **`GSAI_GEOLOGIA`** 💰 | Wskaż punkt → czy w terenie osuwiskowym / zagrożonym (baza SOPO PIG-PIB) + numer osuwiska + stopień aktywności + zalecenie badania geolog.-inż. ⚠️ SOPO pokrywa głównie Karpaty — poza zasięgiem „brak" **≠ „bezpiecznie"**. Podstawa: dane SOPO + Eurokod 7 (PN-EN 1997). | bundle `GSAI-geoportal-test.zip` · `gsai_geologia.py` | 🟡 runtime-test zespołu ([#113](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/113)) |

**Moduł OC (schron)** — osobny bundle `GSAI-schron-test.zip` na release `skrypty-test` w [`gstarcad-ai-zespol`](https://github.com/init3-sentry/gstarcad-ai-zespol), SHA256 `b5f785603c8942c5471fab8335d74686cacd2d0dd2c5261a390739888a5c4578`, zgłoszenie [zespol#114](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/114). Źródła w `narzedzia-do-testow/`: `GSAI_SCHRON.py` + `gsai_schron_core.py`. **To NIE ten sam bundle co Suite GEO.**

| Komenda | Co robi | Plik | Stan |
|---|---|---|---|
| **`GSAI_SCHRON`** 💰 | Checker budowli ochronnej (schron/ukrycie): wskaż zamkniętą polilinię strefy → pole (COM Area) → opcjonalnie liczba osób → sprawdza wymagania WT: min 1 m²/os; wyjścia (>50 os → ≥2, >1000 os → ≥2 poza strefę zagruzowania); wejścia (>300 os → ≥2); podział na strefy (ukrycie ≤300 os, schron S-1 ≤1000 os); dopuszczalność szybu (≤35 m² i ≤10 os); szer. drogi ewakuacyjnej 0,4 m/100 os. **Zakres v1: wymiarowy** (grubości przegród / wentylacja / dojście ≤500 m poza zakresem). Podstawa: rozp. MSWiA z 4.11.2025 (Dz.U. 2025/1548) + ust. z 5.12.2024 o ochronie ludności (Dz.U. 2024/1907). | bundle `GSAI-schron-test.zip` | 🟡 nowy moduł, przed odbiorem praktyka ([#114](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/114)) |
| **`GSAI_DACH`** 🎁 | Generator połaci dachu ze straight-skeleton: wskaż obrys → połacie, kalenice, krawędzie, opisy i strzałki spadków. Native-first + COM fallback (BUG-10-świadome). Generowania połaci z obrysu nie ma nikt. | kod w *powertools* (`GSAI_DACH.py` + `gsai_dach_core.py`, self-test 16/16) | 🟡 **pełny pass zespołu** na 5 typach dachu ([#100](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/100), Tomasz ✓); czeka finalny werdykt Roberta — uwagi z [robert#16](https://github.com/init3-sentry/gstarcad-ai-robert/issues/16) (powiększyć opisy/strzałki, „m²") do wdrożenia. **O krok od ✅.** |
| **`GSAI_PODZIALKA`** | Podziałka liniowa (skala rysunku) na arkuszu. Generatywne → BUG-10-safe. | kod w *powertools* (`GSAI_PODZIALKA.py`) | 🟡 render potwierdzony przez zespół ([#95](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/95), fix nachodzenia „10m"); przed werdyktem Roberta |

> **⚠️ BUG-10 (bug wiązania pygcad, nie nasz):** encje wczytane z ZAPISANEGO pliku DWG wracają jako bazowe `GcDbEntity` → typowane metody geometryczne (`getArea`/`length`) na nich padają. Narzędzia CZYTAJĄCE geometrię z plików klienta (PRZEDMIAR, DLUGOSC) są tym zablokowane; narzędzia GENERUJĄCE (SCHODY, ORNAMENT, IMPORTXYZ) i tabelowe (RENAME_WARSTWY, AUDYTZ) są odporne. Zgłoszone R&D jako top-issue **162444**.

## ⛔ Wycofane — bo GstarCAD ma to natywnie

Zbudowaliśmy je, po czym **sami skasowaliśmy**. Sprawdziliśmy uczciwie i okazało się, że GstarCAD ma te funkcje od lat — tylko mało kto o tym wie.

| Nasze (wycofane) | GstarCAD ma natywnie |
|---|---|
| `GSAI_ZAMIEN_TEKST` | **`FIND`** — i jest bogatszy od naszego |
| `GSAI_EKSPORT_ATRYBUTOW` | **`ATTOUT`** (Express Tools) |
| `GSAI_IMPORT_ATRYBUTOW` | **`ATTIN`** (Express Tools) |
| `GSAI_RENUMERUJ` | **`ATTINC`** — Robert potwierdził (robert#4, 2026-08-05): literki, prefiks, kolejność — wszystko już jest w `ATTINC`. Wątek zamknięty, narzędzie wycofane. |

Warto też znać: **`FLATTEN`** (prostowanie do płaszczyzny), **`TCOUNT`** (numerowanie), **`DATAEXTRACTION`** (dane → tabela/Excel), **`MEASUREGEOM`** (pomiary długości i pól).

**Zasada projektu: nie budujemy tego, co jest już w pudełku.** Dublowanie natywnej funkcji to strata naszego czasu i wprowadzanie klienta w błąd.

## 🧪 Biblioteka wzorców

W [`biblioteka-rag/przyklady/`](biblioteka-rag/przyklady/) leży ~30 plików. Numerowane **01–24** to **przykłady wzorcowe** — materiał uczący sztuczną inteligencję, jak poprawnie pisać kod dla GstarCAD; **działają** i bywają przydatne, ale to pomoce warsztatowe, nie produkty (dlatego bez przedrostka `GSAI_`). Pliki od **25 wzwyż** oraz `GSAI_*.py` to **implementacje narzędzi** skatalogowane w sekcjach wyżej (✅/🟡). `GSAI_CASTPROBE.py` to skrypt diagnostyczny SDK.

Kilka użytecznych z brzegu:

| Komenda | Co robi | Plik |
|---|---|---|
| `ZAKRESKUJ` | Wypełnia wskazaną zamkniętą polilinię kreskowaniem pod skos. | [24_hatch_selected_object.py](biblioteka-rag/przyklady/24_hatch_selected_object.py) |
| `AUDYT_WARSTW` | Zestawienie warstw rysunku — kolory, co włączone/zamrożone. | [04_layer_audit_report.py](biblioteka-rag/przyklady/04_layer_audit_report.py) |
| `ZLICZ_OBIEKTY` | Ile czego jest w rysunku (linie, bloki, teksty…). | [12_count_entities_by_type.py](biblioteka-rag/przyklady/12_count_entities_by_type.py) |

## 🔧 W budowie

> Zbudowane i zwalidowane (walidator API 🟢), ale **bez odbioru runtime na realnym rysunku** — nie idą na stronę. Część (TIN/GRANICA/PROFIL) wisi na BUG-10 (odczyt zapisanych encji), rozwiązywanym na LC.

| Narzędzie | Stan / co robi |
|---|---|
| **`GSAI_TIN`** ⭐ | Warstwice z chmury punktów (Delaunay). Silnik geo wspólny z PROFIL i free-tier GSAI-Geo — fundament linii geodezyjnej. Czyta zapisane punkty Z → rodzina **BUG-10** (pada na plikach klienta). Walidator 🟢, brak runtime-pass; czeka rozwiązanie BUG-10 na LC. |
| **`GSAI_GRANICA`** | Wykaz współrzędnych granicy działki (pole, obwód, tabela). Czyta polilinię z pliku → rodzina **BUG-10**, aktywnie łatane; brak odbioru na rysunku klienta. |
| **`GSAI_PROFIL`** | Profil podłużny z punktów wysokościowych + linia cięcia. Silnik geo wspólny z TIN. Rodzina **BUG-10** (zapisane punkty Z). Walidator 🟢, brak runtime-pass. |
| **`GSAI_PRZEKROJ`** | Przekrój drogowy z parametrów normy. Generatywne → BUG-10-safe. Core self-test 13/13; brak przebiegu zespołu na rysunku. |
| **`GSAI_UMEBLUJ`** | Automatyczne umeblowanie: wstawia bloki mebli wzdłuż ścian. Generatywne. Smoke-test: WC wstawia się poprawnie ([#107](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/107)), zestaw 1/5, pre-Robert. |
| **Podkład rastrowy z georeferencją** | Wstawiony raster sam siada we właściwym miejscu (GstarCAD nie czyta georeferencji z pliku). |
| **Opis współrzędnych punktu** | Opisywanie bez nachodzenia tekstu na siebie. |
| **Formuły w zestawieniach** | Kolumny wyliczane (SUMA = ilość × cena). |
| **Kolejność rysowania wg warstw** | Działająca wersja tego, co w GstarCAD bywa kapryśne. |
| **Szyk „jak w SketchUpie"** | Kopiuj + obróć raz, podaj ×5 — mnoży w danym kierunku. |

---

## Gdzie zgłaszać problemy

- **Zespół wsparcia** (Jakub, Tomasz, Rafał) → komentarz pod właściwym zadaniem w [`gstarcad-ai-zespol`](https://github.com/init3-sentry/gstarcad-ai-zespol).
- **Robert** → panel w [`gstarcad-ai-robert`](https://github.com/init3-sentry/gstarcad-ai-robert).
- **Rysunek, na którym coś się sypie** — to najcenniejszy materiał, jaki możemy dostać. Zawsze **na kopii**, nigdy na oryginale klienta.
