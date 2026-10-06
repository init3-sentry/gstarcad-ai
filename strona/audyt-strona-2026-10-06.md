# Audyt ai.gstarcad.pl — co jest na stronie, a co powinno być (06.10.2026)

Dla Dawida, materiał do zbiorczej informacji dla Eryki. Nic na stronie nie zmieniano.

**Źródła i stan na chwilę audytu (06.10, po 09:53):**
- **Strona na żywo:** katalog `/biblioteka-narzedzi-do-gstarcad/` po „Pokaż więcej” ma 24 karty. Pełną listę potwierdza `wp-json/wp/v2/biblioteka` (24 wpisy `publish`, utworzone 19.08–01.09, ostatnia zmiana 01.09 14:50). Każdą kartę pobrałem i sprawdziłem plik MP4 (HEAD 200).
- **Co powinno być:** `strona/NARZEDZIA-DLA-ERYKI-AKTUALNE.md` (commit `36353b9`, WMS → ✅). Reguła: na stronę idzie tylko ✅.
- **Co dostaje klient:** bundle stable `2026.10.06-64f0cd8` (`/tmp/gsai-build-master/gsai-narzedzia-64f0cd84040e.zip`). Jego `manifest-PL.json` ma **36 kafelków** i jest identyczny z `instalator-gsai/skrypty/manifest-PL.json`. Kafelki testowe (`kafelki-kanal-test.json`) na stable nie idą.
- **Odbiór:** `rejestr-odbioru.json`, który ma tylko 3 wpisy: ILOSCI, ZAZNACZ, WMS. Bramka działa od 26.09, a starsze narzędzia są w snapshot. Do tego kolumna „Zwalidował/Status” w `NARZEDZIA.md` i frontmatter opisów.

## A) Tabela

Film na stronie = MP4 na karcie. „Nowy PL” = gotowy plik w `~/Movies/GSAI-filmy-PL/`.

| Komenda | Na stronie (slug · film) | NARZEDZIA | Kafelek PL na stable | Odbiór | Wniosek |
|---|---|---|---|---|---|
| GSAI_AUDYTZ | tak · `gsai_audytz` · film tak | ✅ | tak | Jakub 29.07 | ZOSTAWIĆ |
| GSAI_CUI | tak · `gsai_cui` · film tak | ✅ | tak | Dawid 23.08 (serwis, „bez kolejki Roberta”) | ZOSTAWIĆ |
| GSAI_DACH | tak · `gsai_dach` · film tak (stary z 09/2026), nowy PL gotowy | ✅ | tak | Robert robert#16. **Opis** przepisany 18.09 i 03.10 czeka na Roberta | ZOSTAWIĆ. Film można podmienić na nowy. Tekst karty zmienić dopiero po odbiorze opisu |
| GSAI_FORMATKA | tak · `gsai_formatka` · film tak | ✅ | tak | Robert robert#22 26.08 | ZOSTAWIĆ |
| GSAI_GRANICA | tak · `gsai_granica` · film tak | ✅ | tak | Robert robert#20 31.08 | ZOSTAWIĆ |
| GSAI_LINIA | tak · `gsai_linia` · film tak | ✅ | tak | Jakub 17.08 (zespol#102) | ZOSTAWIĆ |
| GSAI_PN | tak · `gsai_strzalka_polnocy` · film tak | ✅ | tak | Robert robert#18 26.08 | ZOSTAWIĆ |
| GSAI_PODZIALKA | tak · `gsai_podzialka` · film tak | ✅ | tak | Robert robert#22 26.08 | ZOSTAWIĆ |
| GSAI_POLA | tak · `gsai_pola` · film tak | ✅ | tak | Jakub + Tomasz 17.08 (#102). Opis z 18.09/03.10 czeka na Roberta | ZOSTAWIĆ. Film w produkcji dziś |
| GSAI_POMIAR | tak · `gsai_pomiar` · film tak | ✅ | tak | Jakub 17.08. Opis czeka na Roberta | ZOSTAWIĆ. Film w produkcji dziś |
| GSAI_RZEDNE | tak · `gsai_rzedne` · film tak | ✅ | tak | Dawid 17.09 + Tomasz zespol#164 | ZOSTAWIĆ. Kategoria do zmiany, patrz C |
| GSAI_SCHODY | tak · `gsai_schody` · film tak | ✅ | tak | Tomasz 31.07, Robert ✓ v3 (robert#16) | ZOSTAWIĆ. Film w produkcji dziś |
| GSAI_SLONCE | tak · `gsai_slonce` · film tak | ✅ | tak | Tomasz 06.08 (#79) | ZOSTAWIĆ |
| GSAI_SPADEK | tak · `gsai_spadek` · film tak | ✅ | tak | Jakub 06.08, Robert robert#9 (zamknięte 01.09). Opis 18.09 czeka na Roberta | ZOSTAWIĆ |
| GSAI_WSS | tak · `gsai_wss` · film tak | ✅ | tak | Robert robert#18 26.08 | ZOSTAWIĆ |
| GSAI_XYZ | tak · `gsai_importxyz` · film tak | ✅ | tak | Robert (bez daty w NARZEDZIA) | ZOSTAWIĆ |
| GSAI_ZLICZ | tak · `gsai_zlicz` · film tak | ✅ | tak | Jakub 17.08, Tomasz 02.10 (miniatury). Opis 02.10/05.10 czeka na Roberta | ZOSTAWIĆ. Film w produkcji dziś |
| GSAI_ZNW | tak · `gsai_znw` · film tak | ✅ | tak | Tomasz 29.07 | ZOSTAWIĆ |
| GSAI_WSF | tak · `gsai_wsf` · **film nie** | 🟡 | tak | brak („czeka na finalny zrzut Roberta”) | ZDJĄĆ (reguła ✅), chyba że Dawid da ✅ |
| GSAI_SKL | tak · `gsai_skl` · film tak | 🟡 | tak | brak („na stronę po odbiorze praktyka”) | ZDJĄĆ (reguła ✅), chyba że Dawid da ✅ |
| GSAI_CHROP | tak · `gsai_chrop` · film tak | 🟡 | tak | brak („czeka wizualny werdykt Roberta”, zespol#67) | ZDJĄĆ (reguła ✅), chyba że Dawid da ✅ |
| GSAI_RZUT | tak · `gsai_rzut` · film tak | 🟡 | tak | brak („Do testu”) | ZDJĄĆ (reguła ✅), chyba że Dawid da ✅ |
| GSAI_GEORASTER | tak · `gsai_georaster` · **film nie**, nowy PL gotowy | 🔧 | tak | brak („czeka odbiór praktyka (Robert)”) | ZDJĄĆ (reguła ✅), chyba że Dawid da ✅ |
| GSAI_GML | tak · `gsai_gml` · film tak | 🔧 | tak | brak („czeka odbiór praktyka (Robert)”) | ZDJĄĆ (reguła ✅), chyba że Dawid da ✅ |
| **GSAI_ILOSCI** | **nie** (`/biblioteka/gsai_ilosci/` → 404) | ✅ | tak | N. Kubala 30.09 (rejestr-odbioru) | **DODAĆ.** Film PL gotowy |
| **GSAI_ZAZNACZ** | **nie** (404) | ✅ | tak | Robert robert#24 01.10 (rejestr-odbioru) | **DODAĆ.** Filmu jeszcze nie ma |
| **GSAI_WMS** | **nie** (404) | ✅ od 06.10 09:53 | tak | Dawid 06.10 (rejestr-odbioru) | **DODAĆ.** Film PL gotowy. Paczka leży w `~/Desktop/Eryka-WMS-opinie/` |
| GSAI_TABELKA | nie | 🟡 (wiersz w sekcji 🟡, ale w kolumnie: „✅ ODEBRANE przez Roberta”) | tak | Robert robert#24 04.09/14.09 | CZEKA na Dawida: jeśli wiersz pójdzie do ✅, to DODAĆ (patrz C) |
| GSAI_KOL | nie | 🟡 (wiersz w sekcji 🟡, ale w kolumnie: „✅ DZIAŁA — zatwierdzone przez Roberta 22.09”) | tak | Robert robert#27 22.09 | CZEKA na Dawida, jak wyżej |
| GSAI_AKUSTYKA | nie | 🟡 | tak (tylko PL) | brak („na stronę po odbiorze praktyka”, osoba nie wskazana) | CZEKA na odbiór praktyka |
| GSAI_LEGW | nie | 🟡 | tak | brak | CZEKA na odbiór praktyka (pomysł Roberta, robert#13) |
| GSAI_ODSWIEZ | nie | 🟡 | tak | brak (serwisowe, w teście zespołu) | CZEKA na test zespołu |
| GSAI_SKARPA | nie | 🟡 | tak (PL) | Szczepański: kierunek kreskowania przyjęty 23.09, reszta otwarta | CZEKA na Szczepańskiego |
| GSAI_RURA | nie (404) | 🔧 | **tak** (PL, od `2026.09.24-98aeb8a`) | Kujawski: wersja bez okna przyjęta 24.09. Pytanie o wersję bieżącą wysłane 06.10 08:00 | CZEKA na Kujawskiego, potem decyzja Dawida (sekcja B) |
| GSAI_BLOKI | nie | 🔧 | tak | brak („Czeka odbiór Roberta na jego rysunku”) | CZEKA na Roberta. Film PL gotowy |
| GSAI_ANONIM | nie | 🔧 | tak | brak (wydane „bez czekania na jego werdykt”, Dawid 24.09) | CZEKA na Bobkowskiego |
| GSAI_EWAKUACJA | nie | 🟡 | nie (tylko kanał test) | Tomasz ✓ 02.10 (zespol#192), Robert czeka | CZEKA na Roberta |
| GSAI_ORIENTACYJNY | nie | 🟡 | nie (tylko test) | brak („Odbiór: zgłaszający (Więcan) — nie ma”) | CZEKA na Więcana |
| GSAI_RZUTNIE | nie | **brak wiersza w NARZEDZIA.md** | nie (tylko test) | brak (szkic opisu do odbioru u Dębskiego) | CZEKA. Najpierw trzeba dodać wiersz do NARZEDZIA |

Żadne narzędzie 🔴/⛔ nie ma karty na stronie.

**Bilans:** na stronie jest 18 z 21 narzędzi ✅. Trzy ✅ nie mają karty (ILOSCI, ZAZNACZ, WMS). Sześć kart dotyczy narzędzi, które nie są ✅ (WSF, SKL, CHROP, RZUT, GEORASTER, GML). Klient ma na stable 36 kafelków PL, a karty ma 24 z nich.

## B) RURA i narzędzia, które doszły od ostatniej aktualizacji strony (01.09)

**RURA: dlaczego nie ma karty**
- Status w `NARZEDZIA.md` to 🔧 „W budowie”, a lista dla Eryki trzyma ją poza stroną.
- U klienta narzędzie już jest. Kafelek PL jest na stable od `2026.09.24-98aeb8a`. Poprawkę `1270bd2` (złączone polilinie) zawiera stable `2026.09.28-24f37c5` (REJESTR-WNIOSKOW, wiersz 03.09). Publiczny changelog (`upd.tmsys.pl/changelog/feed.json`) ma 4 wpisy RURA jako „wydane” (24.09–28.09).
- Opis ma `status: gotowy`, ale komentarz w pliku wyjaśnia: „Status tutaj znaczy »dopuszczony do druku«, NIE »odebrany przez praktyka«”.
- Przebieg odbioru:
  - Kujawski przyjął wersję bez okna: „moim zdaniem petarda” (24.09).
  - 27.09 napisał: „Opcja 3 działa super, miód ma moje oczy”. Tego samego dnia o 22:24 zgłosił błąd: przy dwóch złączonych poliliniach rura szła po całej długości.
  - Poprawka trafiła na stable 28.09.
  - Test na jego rysunku (PZT Nagawczyna) 05.10 przeszedł 7/7 (rejestr-opinii `kujawski-rura`).
  - 06.10 o 08:00 poszło pytanie, czy rura rysuje się już tylko między wskazanymi punktami. Mail jest w Wysłanych (`TMSYS:Sent:2076`, „Re: GstarCAD AI — narzędzie »Rura« z Pana zgłoszenia z 3 września”). W indeksie poczty z ostatnich 2 dni nie ma odpowiedzi.
- W `rejestr-odbioru.json` nie ma wpisu RURA. Bramka go nie wymagała, bo RURA była na stable przed 26.09 i siedzi w `odbior-guard-snapshot.json`.
- Wiersz RURA w NARZEDZIA.md jest nieaktualny. Mówi „Trzy poprawki z 24.09 czekają na jego opinię — mail wysłany 24.09 ~21:50”, a nie wspomina błędu z 27.09, poprawki z 28.09 ani pytania z 06.10.
- Droga do karty: Kujawski potwierdza → Dawid zapisuje odbiór (rejestr-odbioru, NARZEDZIA → ✅) → lista dla Eryki się przegenerowuje → karta. Film PL jest gotowy. Zgodę na cytat zbiera się osobno (rejestr-opinii).

**Co doszło po 01.09.** Źródło to changelog-dane (`typ` nowosc / nowy_skrypt / nowe):

| Data wydania | Komenda | Stan dziś | Karta |
|---|---|---|---|
| 09.09 | GSAI_SKARPA | 🟡, stable PL | brak, czeka na Szczepańskiego |
| 09.09 | GSAI_WMS | ✅ od 06.10 | **brak, DODAĆ** |
| 24.09 | GSAI_RURA | 🔧, stable PL | brak, czeka na Kujawskiego |
| 24.09 | GSAI_BLOKI | 🔧, stable | brak, czeka na Roberta |
| 24.09 | GSAI_ANONIM | 🔧, stable | brak, czeka na Bobkowskiego |
| 30.09 | GSAI_ILOSCI | ✅ | **brak, DODAĆ** |
| 01.10 | GSAI_ZAZNACZ | ✅ | **brak, DODAĆ** |
| test (changelog „w_przygotowaniu”) | GSAI_ORIENTACYJNY | 🟡, tylko test | brak |
| test | GSAI_EWAKUACJA | 🟡, tylko test | brak |
| test (brak w changelogu i w NARZEDZIA) | GSAI_RZUTNIE | tylko test, opis `szkic` | brak |

Wydane przed 01.09, a bez karty: TABELKA (nowość 07.08), AKUSTYKA (15.08), LEGW (27.08), KOL (28.08, powrót 19.09), ODSWIEZ (28.08). Statusy są w tabeli A.

## C) Rozbieżności

**Na stronie, choć nie ✅.** 6 kart: WSF, SKL, CHROP, RZUT (🟡) oraz GEORASTER, GML (🔧). Wszystkie mają kafelek na stable. Karty powstały 01.09, czyli przed regułą „tylko ✅” albo niezależnie od niej.

**✅, a brak karty:**
- ILOSCI: ✅ od 30.09.
- ZAZNACZ: ✅ od 01.10.
- WMS: ✅ od dziś. Wydany 09.09.

**Sprzeczność w samym NARZEDZIA.md.** TABELKA („✅ ODEBRANE przez Roberta… »tabelkę mamy zatwierdzoną«”) i KOL („✅ DZIAŁA — zatwierdzone przez Roberta 22.09”) mają w kolumnie statusu ✅, ale ich wiersze stoją w sekcji 🟡. Generator listy dla Eryki bierze sekcję, więc oba narzędzia trafiają do 🟡. Decyzja należy do Dawida: przenieść wiersze albo poprawić kolumnę.

**Karty ✅ z opisem starszym niż narzędzie:**
- Teksty kart są z 01.09.
- Opisy DACH, POLA, POMIAR, SPADEK i ZLICZ przepisano między 18.09 a 05.10. NARZEDZIA.md (sekcja odbioru opisów) mówi przy nich: „Do czasu werdyktu opisy nie idą na stronę”, a werdykt należy do Roberta.
- Przykład: karta DACH nie wspomina okna z pięcioma rodzajami dachu. Opis z 03.10 mówi: „Kod ma okno z pięcioma rodzajami dachu”, a kafelek na stable je wymienia.
- Karta ZLICZ nie mówi o miniaturach bloków ani o przeliczaniu tabeli w miejscu.
- Tekst tych kart zmienić dopiero po odbiorze opisu. Na dziś nie znalazłem w nich zdania sprzecznego z narzędziem.

**Kategoria RZEDNE.** Na stronie jest „Dokumentacja rysunku” (`category-dokumentacja-rysunku`). W manifeście i w NARZEDZIA jest „Architektura i rysunek” („przeniesiony 18.09 wg robert#24”). Pozostałe 23 karty mają kategorie zgodne z manifestem.

**Pozostałości po starych nazwach.** Nie są martwe, wszystko zwraca 200.
- Slug `gsai_importxyz` dla GSAI_XYZ i `gsai_strzalka_polnocy` dla GSAI_PN.
- Pliki filmów `GSAI_IMPORTXYZ.mp4` (XYZ) i `GSAI_RENAME_WARSTWY.mp4` (ZNW).
- Film PN ma w nazwie zepsute kodowanie (`Strza┼eka-Po╠ulnocy.mp4`), ale się odtwarza.

**Bez filmu na karcie:** WSF i GEORASTER. Dla GEORASTER jest gotowy nowy film PL.

**Changelog w hero.** Widżet pokazuje 3 najnowsze wpisy feedu PL. Dziś (06.10) są to BLOKI, BLOKI i ILOSCI, czyli dwa narzędzia bez karty. Feed publicznie wymienia jako „wydane” także RURA, ANONIM, SKARPA, LEGW, KOL, AKUSTYKA, ODSWIEZ i TABELKA, które w bibliotece nie istnieją.

**Licznik.** „Lista dostępnych narzędzi 24” to liczba kart, a nie kafelków u klienta (36).

**Linki** (strona główna, katalog, karta DACH):
- Wszystkie wewnętrzne zwracają 200. Instalator `gstarcad.pl/ftp/2027/GSAI/GSAI-Setup-PL.exe` i PDF instrukcji też 200.
- Link do podręcznika ma schemat `http://www.gstarcad.pl/ftp/2027/GSAI/podrecznik-gsai.pdf`. Przekierowuje na https i zwraca 200. Martwego linku nie znalazłem.
- Aliasy podane na kartach (GSAI_COUNT, AREAS, MEASURE, SLOPE, SUNPATH, LINETYPE, RENAMELAYERS, AUDITZ, BOUNDARY, LEVEL, PROJECTION_SYMBOL, ROUGHNESS, LTSCALELAYER, LAYERSTD_SHORT/FULL, REPAIRCUI, IMPORTGML, STRZALKA_GALERIA) istnieją w kodzie (`skrypty/GSAI_*.py`).

## D) Filmy (2 formaty: 16:9 i 9:16)

Kryterium z `ZASADY-FILMOW.md` (Dawid 04.10): „film pokazuje głównie okno narzędzia i wynik na rysunku, wiersz poleceń poza kadrem”.

**Gotowe (6):**
- Z kartą albo do dodania: DACH, ILOSCI, WMS.
- Bez karty (🔧): BLOKI, RURA, GEORASTER. Na stronę pójdą, gdy dostaną ✅. GEORASTER już ma kartę, ale bez filmu.

**W produkcji dziś:** POLA, ZLICZ, SCHODY, POMIAR (✅, mają kartę, nowy film zastąpi stary) oraz LEGW (🟡, bez karty).

**Mogą powstać, ✅** (okno albo wynik na rysunku):
- Z oknem Tk: PN, SLONCE, SPADEK, PODZIALKA, FORMATKA, RZEDNE, GRANICA, LINIA.
- XYZ: punkty z numerami na rysunku.
- ZAZNACZ: bez okna, ale efekt widać na rysunku. Ramka obraca się z USC podczas ciągnięcia, potem pojawiają się uchwyty.

**Mogą powstać, ale bez karty (nie ✅):**
- Z oknem: TABELKA, KOL, AKUSTYKA.
- Z wynikiem na rysunku: SKARPA, GML, CHROP, RZUT, SKL (zmienia się gęstość kreski).

**Filmu nie robimy:**
- **CUI.** Okno jest, ale skutek, czyli wstążka, widać dopiero po restarcie GstarCAD. Pokazanie go wymaga celowego uszkodzenia pliku interfejsu na maszynie nagraniowej. Rysunek się nie zmienia: „To naprawa interfejsu, nie danych — rysunki zostają nietknięte” (opis). Na karcie zostaje stary film `GSAI_CUI.mp4`.
- **AUDYTZ.** Nie ma okna. Wynikiem jest samo zaznaczenie obiektów, które „Z góry są niewidoczne”, a narzędzie „samo nie zmienia geometrii” (opis). Raport idzie do wiersza poleceń. Na karcie jest stary film.
- **WSS.** Nie ma okna (kod idzie prosto do `_utworz_short`, bez panelu). Wynik widać tylko w menedżerze warstw: „Narzędzie dokłada same warstwy — nie przenosi na nie obiektów” (opis). Na karcie jest stary film.
- **ZNW.** Nie ma okna. Cała rozmowa toczy się w wierszu poleceń (`gcedGetString`), a wynik to nazwy warstw, nic na rysunku. Na karcie jest stary film `GSAI_RENAME_WARSTWY.mp4`.
- **ANONIM.** Zmienia nazwy definicji bloków, a na rysunku nic nie widać.
- **ODSWIEZ.** Narzędzie serwisowe. Skutek widać tylko jako czerwienienie opisów innych narzędzi, więc może się pojawić w filmie POLA albo ILOSCI.
- **WSF: do decyzji Dawida.** Ma panel wyboru branż, ale wynik jest tylko w menedżerze warstw. Film ma sens tylko wtedy, gdy w kadrze będzie menedżer warstw. Dziś karta nie ma filmu.
