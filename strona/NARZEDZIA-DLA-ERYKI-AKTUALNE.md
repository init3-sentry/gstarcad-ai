# Narzedzia na strone - LISTA AUTOMATYCZNA (dla Eryki)

> **Aktualizowane automatycznie z NARZEDZIA.md.** Zerkaj tu **raz dziennie**. Ostatnia aktualizacja: **2026-08-27**.
> Regula: **na strone idzie tylko ✅.** 🟡 = jeszcze nie obiecuj (moze sie zmienic). **NIE edytuj tego pliku recznie** — zrodlem jest `NARZEDZIA.md`.

Gotowych na strone: **15** | w testach: **26** | poza strona (w budowie/wycofane): **13**

## ✅ Na strone (gotowe)

- **`GSAI_AUDYTZ`** — Znajduje i zaznacza obiekty, które „uciekły" w Z≠0 (z góry niewidoczne, psują pomiary w płaskim rysunku). Prostowanie natywnym FLATTEN.
- **`GSAI_CUI`** — „Odzyskaj wstążkę" — naprawa interfejsu GstarCAD, gdy zniknie wstążka/menu (uszkodzony gcad.cuix / porwany rejestr MenuFile). Przywraca z baseline sprzed instalacji albo z 5 zdrowych snapshotów (ring), naprawia rejestrację głównego menu; okno z przyciskiem „Odzyskaj wstążkę" + modal „ZRESTARTUJ GstarCAD". Naprawa interfejsu, nie danych — rysunki nietknięte. Alias globalny: GSAI_REPAIRCUI.
- **`GSAI_FORMATKA`** — Sama ramka rysunkowa ISO 5457 (margines 20 mm lewy / 10 mm pozostałe), formaty A4/A3/A2 (A4 też poziomo), guard „tylko Arkusz", BEZ tabliczki (każda firma ma własną). Natywnie brak w bazie Professional. Generatywne → BUG-10-safe.
- **`GSAI_IMPORTXYZ`** — Plik z Excela/Notatnika ze współrzędnymi → punkty z numerami. Natywnie brak (płatne nakładki = dowód popytu).
- **`GSAI_LINIA`** — Generator złożonego rodzaju linii z wtopionym tekstem (—A—A—); opis wyśrodkowany w przerwie + wybór stylu tekstu. Natywnie brak. Generatywne → BUG-10-safe.
- **`GSAI_PODZIALKA`** — Podziałka liniowa (skala rysunku) na arkuszu — rysowana w mm w Przestrzeni Papieru. Generatywne → BUG-10-safe.
- **`GSAI_POLA`** — Pole i obwód pól/pomieszczeń: zaznacz oknem albo wskaż pomieszczenie → opis w centroidzie + tabela zbiorcza + eksport CSV. Liczy też na pliku ZAPISANYM od klienta (ścieżka COM, obejście BUG-10). Wchłonęło ZESTAWIENIE i PRZEDMIAR (konsolidacja, Robert ✓).
- **`GSAI_POMIAR`** — Pomiar z opisem: długości + odległość punkt-punkt, „obwód" w opisie zamkniętej polilinii, linia przerywana skąd-dokąd, przełącznik orientacji opisu. Natywnie brak takiego złożenia.
- **`GSAI_RENAME_WARSTWY`** — Hurtowa zmiana nazw warstw wzorcem (find→replace w środku nazwy) z obsługą kolizji. Natywnie GstarCAD tego nie ma — lukę potwierdził na piśmie QA Manager Autodesku (ADR 08). Wartość = hurt/wzorzec, nie pojedyncza warstwa.
- **`GSAI_SCHODY`** — Generator schodów (rzut / łuk / przekrój; tryby biegu) — „wow": schody w GstarCAD za darmo. Rysuje też po ponownym otwarciu pliku (generatywne → odporne na BUG-10).
- **`GSAI_SLONCE`** — Diagram nasłonecznienia / ścieżka słońca (biegunowy wykres): szerokość geo + data → horyzont, pierścienie wysokości, azymuty N/E/S/W, ścieżka słońca + przesilenia/równonoc. Okno z dropdownem 18 miast wojewódzkich + ręczna szerokość. v2 06.08: legenda „jak czytać" (praktyk brał to za mapę cienia). Generatywne → BUG-10-safe. Spina z Linijką Słońca. GSAI_SUNPATH = alias.
- **`GSAI_SPADEK`** — Strzałka spadku + wartość (%/‰/°/1:n) — dachy, tarasy, odwodnienie; tryb ręczny albo auto z różnicy wysokości. Natywnie brak. Generatywne → BUG-10-safe.
- **`GSAI_STRZALKA_POLNOCY`** — Ozdobna strzałka północy — 6 stylów dwutonowych (prosta/strzałka/romb/róża wiatrów/kompas geodezyjny/iglica), panel wyboru z podglądem + wysokość + klik. v2 06.08: wynik jako blok na bieżącej warstwie (obrót przez ROTATE, przesuń/kasuj jako jeden obiekt). Natywnie brak (GstarCAD ma tylko COMPASS/NORTHDIRECTION). Generatywne → BUG-10-safe. GSAI_STRZALKA_GALERIA = wszystkie naraz.
- **`GSAI_WSS`** — Warstwy Standard Short — praktyczny zestaw 42 warstw jednym poleceniem (ustawienia praktyka wg wzorca Roberta: grupy A/E/S/L/W + systemowe, gotowe kolory ACI+RGB, typy linii i grubości pod codzienną robotę). Zakłada tylko te, których w rysunku jeszcze nie ma. Natywnie brak. Generatywne → BUG-10-safe. Alias globalny: GSAI_LAYERSTD_SHORT.
- **`GSAI_ZLICZ`** — Zliczanie obiektów wg kryterium (warstwa/blok/typ) → tabela na rysunku; bloki dynamiczne liczone po nazwie efektywnej (nie po anonimowej *U###).

## 🟡 W testach — jeszcze NIE na strone

- `GSAI_AKUSTYKA` — Kalkulator czasu pogłosu RT60 + ocena zgodności z PN-B-02151-4; tabela wyników na rysunku.
- `GSAI_BUDYNKI` — Obrysy budynków w okolicy wskazanego punktu (EGiB/BDOT10k).
- `GSAI_CHROPOWATOSC` — Symbol chropowatości powierzchni (haczyk 60°, warianty usunięcia materiału, półka na dane).
- `GSAI_DACH` — Generator połaci dachu ze straight-skeleton: wskaż obrys → połacie, kalenice, krawędzie, opisy i strzałki spadków. Native-first + COM fallback (BUG-10-świadome). Generowania połaci z obrysu nie ma nikt.
- `GSAI_DLUGOSC` — Suma długości; _OPIS dokłada etykietę na rysunku.
- `GSAI_DLUGOSC_OPIS` — Suma długości; _OPIS dokłada etykietę na rysunku.
- `GSAI_DZIALKI` — Wskaż punkt → obrys działki + numer + powierzchnia (ULDK/EGiB). Podkład.
- `GSAI_GEOLOGIA` — Wskaż punkt → czy w terenie osuwiskowym / zagrożonym (baza SOPO PIG-PIB) + numer osuwiska + stopień aktywności + zalecenie badania geolog.-inż. ⚠️ SOPO pokrywa głównie Karpaty — poza zasięgiem „brak" ≠ „bezpiecznie". Podstawa: dane SOPO + Eurokod 7 (PN-EN 1997).
- `GSAI_GEOPORTAL` — Panel checkboxów: wskaż punkt → zaciąga zaznaczone warstwy. Agregator pozostałych narzędzi geo.
- `GSAI_LEGENDA_WARSTW` — Wstawia legendę warstw jako tabelę na rysunku: nazwa + próbka koloru + próbka typu linii (graficznie) + szerokość + druk + opis. Pomysł Roberta (robert#13). Natywnie brak. Generatywne → BUG-10-safe.
- `GSAI_MEBLE` — Rozbudowany katalog ~60 symboli (kuchnia, sanitariat, meble pokojowe) wstawianych jako bloki.
- `GSAI_NUMERACJA` — Automatyczne wstawianie i inkrementacja numerów rysunków/arkuszy.
- `GSAI_POG` — Plan Ogólny gminy: strefa planistyczna + wskaźniki (maks. intensywność, maks. % zabudowy, maks. wysokość, min. pow. biologicznie czynna) + flaga Obszaru Uzupełnienia Zabudowy + policzona koperta chłonności z pola działki. Źródło: usługa PlanyOgolneGmin (WMS). Podstawa: reforma planistyczna (ust. 7.07.2023) + rozp. MRiT 8.12.2023 + WT §39 (Dz.U. 2022/1225). ⚠️ Mało gmin ma uchwalony POG (Studia obowiązują do 31.08.2026) — „brak POG" to poprawny wynik. Spina dawne narzędzia chłonność + POG.
- `GSAI_PRZEJEZDNOSC` — Analiza przejezdności (swept-path): obwiednia pojazdu miarodajnego na trasie + ścięcie zakrętu (śmieciarka, naczepa, autobus).
- `GSAI_RZEDNE` — Znacznik rzędnej wysokościowej na przekroju/rzucie — wskaż punkt bazowy ±0,000 (DOWOLNY, nie początek układu), potem kolejne punkty; auto-odczyt Y liczy różnicę. Grot otwarty/zamknięty-w-połowie-czarny wg PN-B-01025:2004 §3.5, każdy znacznik = BLOK. Natywnie brak dedykowanego. Generatywne.
- `GSAI_SCHRON` — Checker budowli ochronnej (schron/ukrycie): wskaż zamkniętą polilinię strefy → pole (COM Area) → opcjonalnie liczba osób → sprawdza wymagania WT: min 1 m²/os; wyjścia (>50 os → ≥2, >1000 os → ≥2 poza strefę zagruzowania); wejścia (>300 os → ≥2); podział na strefy (ukrycie ≤300 os, schron S-1 ≤1000 os); dopuszczalność szybu (≤35 m² i ≤10 os); szer. drogi ewakuacyjnej 0,4 m/100 os. Zakres v1: wymiarowy (grubości przegród / wentylacja / dojście ≤500 m poza zakresem). Podstawa: rozp. MSWiA z 4.11.2025 (Dz.U. 2025/1548) + ust. z 5.12.2024 o ochronie ludności (Dz.U. 2024/1907).
- `GSAI_SYMBOL_RZUTOWANIA` — Tabliczkowy symbol metody rzutowania 1./3. kąta (ISO 5456-2) — ścięty stożek w dwóch widokach. Natywnie brak. Generatywne.
- `GSAI_TABELKA` — NOWA 07.08 — połowa rozdziału GSAI_FORMATKA: tabliczka rysunkowa ISO 7200 (PL) + pas właściciela (logo + Biuro) jako osobny blok ATTDEF, dla tych bez własnej tabliczki. Szerokość 180 mm (≤180mm, wymóg Roberta), wysokość 57mm. Punkt wstawienia = prawy dolny narożnik (klik, tabliczka rozwija się w lewo/górę — dosuwalna do dowolnego rogu ramki). Guard „tylko Arkusz". Generatywne → BUG-10-safe. Styl TTF GSAI_PL dla polskich znaków.
- `GSAI_TRASA` — Wskaż polilinię przyłącza → wykaz przeciętych działek (obrysy + numery) w rysunku.
- `GSAI_WEKTORYZUJ` — Skan rastrowy → polilinie, lokalnie.
- `GSAI_WLADANIE` — Wskaż punkt → kto włada działką (Skarb Państwa / gmina / osoba fizyczna — bez nazwisk, RODO) + ścieżka „do kogo się zwrócić". Źródło: KIEG (grupa_rejestrowa). Podstawa: §14 rozp. EGiB (Dz.U. 2024/219). Hak — pojedyncza działka.
- `GSAI_WSF` — Warstwy Standard Full — pełny branżowy zestaw warstw wg normy (A/K/instalacje/Z + systemowe), kolory kolejne z palety indeksu ACI 1–255 do własnego dostrojenia. Panel wyboru branż. Rodzeństwo GSAI_WSS (Short). Natywnie brak. Generatywne → BUG-10-safe. Alias globalny: GSAI_LAYERSTD_FULL.
- `GSAI_WYKAZ` — Wskazana działka + sąsiedzi graniczni → tabela właścicieli/instytucji na rysunku.
- `GSAI_WYSOKOSC` — Etykieta wysokości H z Numerycznego Modelu Terenu (GUGiK).
- `GSAI_ZABYTKI` — Wskaż punkt → czy objęty ochroną konserwatorską (NID: zabytek nieruchomy / archeologiczny / UNESCO) + numer rejestru + „wymagane pozwolenie WKZ". Źródło: usługi INSPIRE NID (usluga.zabytek.gov.pl). Podstawa: art. 36 ust. z 23.07.2003 o ochronie zabytków.
- `GSAI_ZNAKI` — Tarcze pionowych znaków drogowych (grupy A/B/C/D) + znak B-33 wg Dz.U. 2003/2181; wynik jako blok.

## 🔧 W budowie — poza strona

- `GSAI_GEORASTER` — Podkład rastrowy sam siada na prawdziwych współrzędnych. Czyta georeferencję z kompletu źródeł: world file (.tfw/.jgw/.pgw/.wld…), tagi GeoTIFF w samym .tif (skala+tiepoint albo macierz transformacji, układ z GeoKeyDirectory) oraz ESRI .aux.xml + .prj. Osadza natywnym IMAGEATTACH (punkt/skala/obrót z modelu) → omija buga słownika obrazów, na którym utknął GSAI_ORTOFOTO (BUG-05 / downcast 162444). GUI + raport georeferencji + odczyt współrzędnych wskazanego punktu. GstarCAD natywnie tego nie potrafi (ma IMAGEATTACH bez czytania georeferencji). Nowe 2026-08-26. Self-test offline 15/15 (world-file / GeoTIFF / aux.xml); brak runtime-pass na realnym rysunku — czeka odbiór praktyka (Robert). Opis (2 wersje) = szkic do odbioru Roberta.
- `GSAI_GML` — Import GML EGiB (ewidencja gruntów i budynków): rysuje działki / budynki / kontury użytków / klasy jako zamknięte polilinie i punkty graniczne na warstwach EGIB_*. Czyta układ z srsName, dla PL-2000 / PL-1992 zamienia osie (X=E, Y=N), obsługuje Polygon / Surface-patches / MultiSurface z otworami; opcja przesunięcia do punktu bazowego (wsp. rzędu 7 mln). Alias globalny GSAI_IMPORTGML. MVP. Silnik (gsai_gml_core) przetestowany na realnym pliku EGiB (zsk_2025.gml: 14 działek / 7 budynków / 92 punkty / 89 użytków / 63 klasy, EPSG 2178, swap OK); samo rysowanie w GstarCAD bez runtime-pass — czeka odbiór praktyka (Robert). Opis (2 wersje) = szkic do odbioru Roberta.
- `GSAI_GRANICA` — Wykaz współrzędnych granicy działki (pole, obwód, tabela). Czyta polilinię z pliku → rodzina BUG-10, aktywnie łatane; brak odbioru na rysunku klienta.
- `GSAI_PROFIL` — Profil podłużny z punktów wysokościowych + linia cięcia. Silnik geo wspólny z TIN. Rodzina BUG-10 (zapisane punkty Z). Walidator 🟢, brak runtime-pass.
- `GSAI_PRZEKROJ` — Przekrój drogowy z parametrów normy. Generatywne → BUG-10-safe. Core self-test 13/13; brak przebiegu zespołu na rysunku.
- `GSAI_TIN` — Warstwice z chmury punktów (Delaunay). Silnik geo wspólny z PROFIL i free-tier GSAI-Geo — fundament linii geodezyjnej. Czyta zapisane punkty Z → rodzina BUG-10 (pada na plikach klienta). Walidator 🟢, brak runtime-pass; czeka rozwiązanie BUG-10 na LC.
- `GSAI_UMEBLUJ` — Automatyczne umeblowanie: wstawia bloki mebli wzdłuż ścian. Generatywne. Smoke-test: WC wstawia się poprawnie (#107), zestaw 1/5, pre-Robert.

## ⛔ NIE umieszczac (wycofane / zastapione natywnym GstarCAD)

- `GSAI_EKSPORT_ATRYBUTOW`, `GSAI_IMPORT_ATRYBUTOW`, `GSAI_ORNAMENT`, `GSAI_PRZEDMIAR`, `GSAI_RENUMERUJ`, `GSAI_ZAMIEN_TEKST`
