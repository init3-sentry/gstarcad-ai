# Mapa drogowa projektu gstarcad-ai

Wersja: **2.0 — 30 lipca 2026** (pełne przepisanie; zastępuje wersję 1.0 z 30 czerwca 2026).
Autor: Dawid Jakubowski (PM produktu GstarCAD nationwide, TMSys) + Claude (Anthropic).

Dokument jest naszym wewnętrznym kompasem strategicznym. Pokazuje co, kiedy i w jakiej kolejności robimy. Zmieniany jest świadomie i z datą — żeby było widać, kiedy coś się przesunęło i dlaczego. **Każda kolejna wersja jest pełnym przepisaniem z aktualną datą** (nie doklejamy poprawek do starego tekstu — przepisujemy całość, a poprzednia wersja zostaje w historii repozytorium).

**Źródła wiążące tej wersji:** wewnętrzne decyzje kierunkowe z 16 lipca 2026 (kierunek, skala, dystrybucja — po webinarze premiery 2027) oraz z 24 lipca 2026 (model freemium + ochrona płatnego pakietu). Gdziekolwiek pamięć zespołu mówi inaczej — obowiązuje ten plan.

---

## Co się zmieniło względem wersji 1.0 (i dlaczego)

Wersja 1.0 zakładała, że **produktem jest aplikacja-czat za żetony** (`ai.gstarcad.pl` jako okno rozmowy z modelem, doładowania, ASKAI jako płatny element kliencki), a darmowe treści to warstwa adopcyjna, która ma się z czasem samofinansować z doładowań.

Miesiąc pracy i webinar premiery 2027 to odwróciły. Cztery twarde ustalenia:

1. **Zero z 53 pytań na czacie webinaru nie dotyczyło AI.** Baliśmy się fali „kiedy dostanę tę AI". Nie padło ani jedno pytanie — ludzie pytali o multilinie, XLINE, PURGE, Linuksa. Rama „AI jest po naszej stronie, nie w rękach klienta; klient dostaje gotowe narzędzia, nie przycisk AI" zadziałała dokładnie tak, jak ją zaprojektowaliśmy. To dowód empiryczny, nie opinia.
2. **Praktyczna wartość czatu-za-żetony jest znikoma, a ryzyko realne.** Model generujący kod pygcad bywa w błędzie (potwierdzone na własnym podwórku: mając walidator, komplet stubów i wzorce, wysłaliśmy zespołowi zepsute narzędzie — BUG-06). Kreślarz, któremu czat da niedziałający kod, nie powie „czat się pomylił" — powie „GstarCAD nie działa" i zadzwoni na pomoc. Do tego koszt bez sufitu i brak przychodu po drugiej stronie.
3. **Arytmetyka mówi, gdzie jest pieniądz.** Licencja GstarCAD to 639–959 EUR. Roczny suite geodezyjny ≈ 80 EUR. **Jedna osoba, która wybierze GstarCAD zamiast ZWCAD dzięki naszym narzędziom, jest warta osiem lat abonamentu geo.** Geodetów jest garstka, kreślarzy — cały rynek. Darmowe narzędzia to nie koszt adopcji; to najlepiej zwracająca się dźwignia sprzedaży licencji, jaką mamy.
4. **Prezes Tomasz chce popularnej płatnej nakładki na subskrypcji.** Odpowiadamy na to jednym płatnym pakietem premium — ale zbudowanym tak, żeby nie kanibalizował ramy z punktu 1.

**Nowy model w jednym zdaniu:** darmowe narzędzia `GSAI_*` **są produktem** (magnes, który wygrywa wybór „GstarCAD, nie ZWCAD" i napędza sprzedaż licencji); **AI jest naszą narracją marketingową**, nie funkcją w rękach klienta („te narzędzia napisała AI — dała nam skrzydła, aplikacje piszemy w tygodnie, nie w lata; my je sprawdziliśmy, zanim je Państwu daliśmy"); **jedyny bezpośredni przychód to jeden płatny pakiet premium** przez nasz własny klucz aktywacyjny; **retencję trzyma konieczność aktualizacji** (narzędzia działają na najnowszej bieżącej wersji). Czat-za-żetony i plugin ASKAI **nie są zabite — są zaparkowane** i nie wchodzą do premiery.

---

## Cele projektu

Krótko: **uczynić GstarCAD najbardziej rozpoznawalnym systemem CAD w segmencie cenowym w Polsce — poprzez darmowe narzędzia, których konkurencja (ZWCAD, BricsCAD) nie ma, opatrzone wiarygodną narracją, że napisała je sztuczna inteligencja.** Narzędzia są bronią w wyborze zakupowym; AI jest powodem, dla którego o nas mówią; jeden płatny pakiet jest strumieniem przychodu obok sprzedaży licencji. Z tego wynikają cztery mierzalne wskaźniki sukcesu:

1. **Sprzedaż licencji napędzana produktem.** Co najmniej dwustu projektantów CAD spoza dotychczasowej bazy TMSys ma w ciągu pierwszych dwunastu miesięcy skontaktować się z TMSys w sprawie zakupu licencji GstarCAD, wskazując jako pierwotne źródło nasze narzędzia, stronę `ai.gstarcad.pl`, treści wideo albo materiały branżowe projektu. **To jest wskaźnik nadrzędny** — cała reszta mu służy.
2. **Adopcja darmowych narzędzi.** Co najmniej tysiąc unikalnych pobrań pakietu narzędzi (przez instalator albo pojedynczo) w ciągu pierwszych trzech miesięcy od uruchomienia strony. Pobranie i realne użycie narzędzia to moment, w którym kreślarz przekonuje się, że GstarCAD robi coś, za co konkurencja bierze osobno.
3. **Pozycja w dyskusji branżowej.** GstarCAD ma być rozpoznawalnie wymieniany jako system z natywnym Pythonem i z narzędziami napisanymi przez AI w co najmniej pięciu znaczących publikacjach branżowych (portale, blogi, materiały wideo niezależnych projektantów) w ciągu pierwszego roku.
4. **Przychód z pakietu premium.** Płatny pakiet premium (funkcje geo-przestrzenne, framowane po funkcji nie po zawodzie) ma w ciągu pierwszych sześciu miesięcy od premiery pakietu osiągnąć liczbę płatnych aktywacji pokrywającą koszt jego utrzymania i rozwoju, z dodatnią marżą. To odpowiedź na oczekiwanie prezesa Tomasza dotyczące płatnej nakładki na subskrypcji.

Wskaźnik pierwszy jest priorytetowy. Drugi i trzeci są dźwigniami pierwszego. Czwarty jest samodzielnym, ale wtórnym strumieniem — nie wolno mu podmyć wskaźnika pierwszego (dlatego pakiet premium jest odrębny i wąski, a nie „przełącznik płatności" doklejony do darmowych narzędzi).

---

## Filary strategii — cztery zdania, które muszą się zgadzać w każdym materiale

Zanim ktokolwiek napisze zdanie na stronę, do zespołu, do prasy albo do klienta — ma pasować do tych czterech filarów. Jeśli nie pasuje, to nie jest nasz komunikat.

1. **Narzędzia, nie przycisk AI.** Klient dostaje gotowe komendy, które rozwiązują jego konkretny ból (400 warstw, import punktów, zestawienie). Nie dostaje okna, w którym sam prosi AI o kod. AI pracuje po naszej stronie i pod naszą kontrolą.
2. **AI jako wyjaśnienie, nie obietnica.** Najpierw narzędzie zadziała, potem klient przeczyta, że napisała je AI. „Pokazali", nie „obiecali". Zdanie nośne: *„Te narzędzia napisała sztuczna inteligencja. My je sprawdziliśmy, zanim je Państwu daliśmy."*
3. **Darmowe = magnes na licencję; jeden płatny pakiet = przychód obok.** Nie mieszamy tych dwóch. Darmowe narzędzia nigdy nie mają bramki płatności. Płatny pakiet ma własny klucz i własną tożsamość.
4. **Kopiowalność darmowych narzędzi jest atutem.** Nakładka to embedded-Python — martwy plik `.py` bez GstarCAD, nie odpali się w AutoCAD ani ZWCAD. Skopiowana nakładka jest więc **wirusową demonstracją** „GstarCAD robi to, za co konkurencja bierze 350 dolarów za plugin". Nie chronimy darmowych narzędzi DRM-em — chcemy, żeby krążyły.

---

## Etapy projektu

Praca podzielona jest na etapy o konkretnych kryteriach zaliczenia. Etapy częściowo się nakładają — biblioteka wiedzy i narzędzia rosną równolegle, instalator domyka łańcuch dostawy, strona jest bramą do premiery. Kolejność krytyczna (za decyzją 06 §7):

> **`GSAI_XYZ` (utwardzenie) → WARSTWY → INSTALATOR → strona-pobieralnia → zliczanie/tabelki → (geodezja / wektoryzacja / ASKAI = zaparkowane).**

### Etap 0 — PoC pluginu ASKAI (ZAMKNIĘTY, historyczny)

**Status: ✅ ZALICZONY (8 lipca 2026).** Plugin PoC rejestruje komendę `ASKAI` przez dekorator `@command`, ładuje się przez `APPLOAD`, otwiera okno `tkinter` bez zamrażania GstarCAD, wykonuje wywołanie HTTPS do backendu i strumieniuje odpowiedź; przycisk „Wykonaj tutaj" wykonuje wygenerowany kod w bieżącym rysunku. Zweryfikowane na GstarCAD 2026 Plus i 2027 Plus. Backend PoC wdrożony (prywatny; działa na realnym kluczu Anthropic — testy prowadzone na prywatnym kluczu Dawida).

**Rola w wersji 2.0:** PoC potwierdził wykonalność — i na tym poprzestajemy. **Plugin ASKAI jako produkt kliencki jest zaparkowany** (patrz „Co jest zaparkowane"). Wykonalność mamy udowodnioną; wracamy do niej, gdy narzędzia zbudują wiarygodność, która kupuje prawo do eksperymentu z czatem w środku CAD.

### Etap 1 — Biblioteka wiedzy o pygcad (silnik produkcji narzędzi)

**Status: w toku, zaawansowany.**

**Cel:** utrzymać żywą, empirycznie zwalidowaną bazę wiedzy o API pygcad, dzięki której model AI (i my) piszemy kod, który **działa w GstarCAD za pierwszym razem**, zamiast halucynować kod w stylu AutoCAD. To jest silnik, który napędza wszystkie pozostałe etapy — i jednocześnie dowód narracji „AI potrafi oprogramować ten CAD".

**Zmiana ramy vs 1.0:** biblioteka nie jest już produktem wystawianym klientowi jako „opublikowany GPT / projekt Claude do samodzielnego promptowania". Jest **naszym wewnętrznym narzędziem produkcyjnym**. Klient nigdy nie widzi surowego API — dostaje gotowe komendy.

**Kryteria bieżące:**
- [`biblioteka-rag/api-signatures-reference.md`](biblioteka-rag/api-signatures-reference.md) — żywa referencja, która **rośnie z każdym narzędziem** (reguła żywej bazy). Sygnatury oznaczane statusem: 🟢 zwalidowane na żywo w GstarCAD, 🟡 wg dokumentacji, ⛔ zakazane z alternatywą (rejestr pułapek: `.cast()` = BUG-07, `gcedGetReal` = BUG-06, downcast po ponownym otwarciu = BUG-10).
- [`biblioteka-rag/przyklady/`](biblioteka-rag/przyklady/) — zwalidowane wzorce kodu. „Zwalidowany" znaczy **uruchomiony w GstarCAD**, nie „napisany wg dokumentacji" — wzorzec nieuruchomiony jest gorszy niż jego brak, bo model ufa mu bardziej niż stubom.
- Wewnętrzny rejestr bugów SDK zgłaszany zbiorczo do R&D GstarSoft.

### Etap 2 — Darmowe narzędzia `GSAI_*` (to jest produkt)

**Status: w toku — trzon workhorse gotowy, ciekawostki dochodzą.**

**Cel:** zbudować katalog darmowych komend, które rozwiązują realne, powtarzalne bóle projektanta — i które konkurencja w tym segmencie cenowym oferuje płatnie albo wcale. To jest właściwy produkt projektu.

Katalog ma dwie warstwy o różnej funkcji marketingowej:

- **Workhorse — narzędzia „skalowe".** Rozwiązują ból, o który ludzie proszą wprost (dowód popytu z ankiety powebinarowej). Prowadzą w komunikacji, bo popyt jest wyartykułowany. Rdzeń: `GSAI_WARSTWY` (hurtowe czyszczenie + reguła + raport, czego PURGE nie ruszy i dlaczego — demo „437 warstw → 12, jedna komenda"), `GSAI_XYZ`, `GSAI_ZAMIEN`, `GSAI_RENUMERUJ`, `GSAI_PRZEDMIAR`, `GSAI_SCHODY`.
- **Ciekawostki — narzędzia „o, nie wiedziałem, że w CAD tak można".** Nie ściągają funkcjonalnością (bo popyt jest nieartykułowany — nikt o nie nie prosi, bo nikt nie pomyślał, że się da), ale robią efekt „wow" na stronie i w wideo, i pokazują, że AI naprawdę dała nam skrzydła. Trzon: `GSAI_ORNAMENT` (generator wzorów — algorytm rysuje, każdy user dostaje inny zestaw; to jest „idea AI" pokazana wprost), `GSAI_SLONCE` (diagram nasłonecznienia), `GSAI_POLNOC` + `GSAI_PODZIALKA` (ozdobna strzałka północy i podziałka skali).

**Native-first jest obowiązkowy przed każdym narzędziem.** Budujemy tylko to, czego GstarCAD nie umie zrobić **hurtem według reguły** (nie to, czego nie ma w ogóle — bo referencja 697 komend pokazała, że wiele „luk" było fałszem z braku znaleziska). Kryterium: „jest, ale ręcznie, 437 razy" = realny ból; „nie ma i nikt nie prosi" = nie prowadzić tym.

**Kryteria zaliczenia:**
- Trzon workhorse (min. 5 narzędzi) przetestowany przez zespół na realnych rysunkach klientów, w tym scenariusz **zapisu i ponownego otwarcia** (łapie BUG-10).
- Min. 3 ciekawostki gotowe do wideo/strony.
- Każde narzędzie: kod `.py` + polski opis + zrzut demo. Katalog statusów: [`gstarcad-ai/NARZEDZIA.md`](NARZEDZIA.md) jako SoT.
- Warunek startu strony (za 06 §6): **co najmniej trzy działające narzędzia.**

### Etap 3 — Instalator (łańcuch dostawy bez dziur)

**Status: w budowie — komponenty rozpoznane empirycznie, brak wersji end-to-end.**

**Cel:** klient klika jeden instalator i dostaje działające komendy w GstarCAD, **nie widząc nigdy Pythona ani `APPLOAD`.**

> instalator → cicho stawia Pythona 3.11.8 z PATH → kopiuje narzędzia → wpisuje je do Zestawu Startowego → dokłada menu w CUI → użytkownik otwiera GstarCAD i ma komendy

**Rozpoznanie empiryczne (06 §4, zmierzone na LC):**
- **Python + PATH:** cicha instalacja oficjalnym instalatorem (`/quiet InstallAllUsers=1 PrependPath=1`). ⛔ **PATH przez rejestr odrzucony** — trzy pułapki (REG_EXPAND_SZ, WM_SETTINGCHANGE, `setx` ucina na 1024 znakach) niszczą ludziom system; oficjalny instalator robi to poprawnie sam.
- **Zestaw Startowy = dwie wartości w rejestrze** (`...\R27\pl-PL\Profiles\<profil>\Dialogs\Appload\Startup`: `NumStartup` + `0Startup`). Ładuje `.py` bez `APPLOAD`. ⚠️ Trzy pułapki wywracające instalator po cichu: pisać do `HKU\<SID>` **nie** `HKCU` (instalator działa jako admin), wykrywać wersję+język w ścieżce (nie zaszywać), wyliczać aktywny profil, **doliczać** `NumStartup` do istniejących (nie nadpisywać makr klienta).
- **Menu:** `.cuix` to ZIP — generujemy skryptem, wersjonujemy, oglądamy w diffie. Dokładamy jako **częściowy plik dostosowania** (tą samą drogą, którą producent wnosi Express Tools).
- 🔴 **Bundle NIE ładuje `.py`** — sprawdzone, negatywne. Stąd **dwa mechanizmy**: Zestaw Startowy wnosi Pythona, częściowy `.cuix` wnosi menu.
- **Reguła domu — lazy import:** Zestaw Startowy ładuje plik przy każdym otwarciu rysunku. Ciężkie biblioteki (`numpy`, `PIL`) importujemy **wewnątrz** funkcji komendy, nie na górze modułu — inaczej klient uzna, że GstarCAD zwolnił po naszej instalce.

**Kryteria zaliczenia:**
- Wersja end-to-end: czysty Windows → instalator → GstarCAD z działającymi komendami, bez ani jednego ręcznego kroku.
- Instalator wykrywa (nie zaszywa) wersję, język, edycję i profil; poprawnie pisze do gałęzi użytkownika.
- Test na czystej maszynie Windows przez zespół (każdy na swojej), min. dwie edycje.
- Podpisany plik `.exe` dla klienta końcowego (klik, zero GitHuba, zero paste).

### Etap 4 — Strona `ai.gstarcad.pl` (pobieralnia) i premiera

**Status: oczekuje na trzy działające narzędzia + instalator.**

**Cel:** publiczna strona, z której klient pobiera narzędzia. **To pobieralnia, nie czat-aplikacja** (zmiana kluczowa vs 1.0).

**Zasady strony (06 §6):**
- **Nie zaczynamy od „AI".** Zaczynamy od narzędzi. Kreślarz z 400 warstwami nie kliknie w „AI" — kliknie w „posprzątaj warstwy". Dopiero gdy mu zadziała, przeczyta, jak to powstało.
- **Jedno zadanie strony:** przycisk „Pobierz", trzy zdania co to robi, 20-sekundowy film z warstwami. **Bez rejestracji, bez maila** — to przynęta na adopcję, nie lead-gen.
- ⛔ **Nie linkujemy repozytorium.** Repo pokazuje kreślarzowi (i ZWCAD-owi) naszą kuchnię: kod, notatki, rejestr błędów. Człowiek, który chciał posprzątać warstwy, widzi ścianę i wychodzi.
- **Uczciwość wbudowana w konstrukcję.** Na stronie nie ma Roberta, który powie zastrzeżenie na żywo — więc zdanie nośne („napisała AI, my sprawdziliśmy") i historia czterech skasowanych narzędzi-dubli muszą być częścią przekazu, nie dopiskiem.

**Synchronizacja z premierą:** publiczna premiera zsynchronizowana z **polską premierą GstarCAD 2027** (druga połowa września 2026 — TMSys konsekwentnie nie robi premier wakacyjnych). Jeden komunikat: „nowa wersja + narzędzia, które napisała AI". Ścieżka krytyczna do tego dnia: darmowe narzędzia (mamy) + instalator + pobieralnia + narracja AI.

**Kryteria zaliczenia:**
- Domena aktywna, prowadzi do strony-pobieralni w pełnej, pięknej polszczyźnie.
- Pobranie działa bez rejestracji; instalator i/lub pojedyncze narzędzia dostępne.
- Film demonstracyjny (warstwy) i teksty zgodne z czterema filarami.
- Regulamin i klauzula RODO zatwierdzone przez prawnika TMSys (o ile pobieranie zbiera jakiekolwiek dane — domyślnie nie zbiera).

### Etap 5 — Płatny pakiet premium + własny klucz aktywacyjny

**Status: kierunek ustalony (09), skład i system kluczy do zaprojektowania.**

**Cel:** jeden płatny pakiet — odpowiedź na oczekiwanie prezesa Tomasza dotyczące płatnej nakładki na subskrypcji — który daje przychód **obok** sprzedaży licencji, nie zamiast darmowego magnesu.

**Zasady (09):**
- **Framowanie po funkcji, nie po zawodzie.** Roboczo „geodezyjny", ale etykieta „geodezyjne" odcina połowę odbiorców. Funkcje są dwuadresowe: georeferencja, import-eksport punktów, pobieranie obrysów sąsiednich działek, mapy, warstwice — potrzebuje ich geodeta **i** architekt. O przynależności narzędzia decyduje „ile realnej roboty oszczędza", nie zawód.
- **Własny klucz aktywacyjny, niezależny od mechanizmu licencyjnego GstarCAD.** Badanie na .240 (09) zamknięte twardo: terytorialny entitlement licencji GstarCAD jest praktycznie nieczytelny (zaszyfrowany trusted storage / `gcad.lic`). Czytelne z zewnątrz tylko język instalacji + edycja — za mało jako dyskryminator terytorium. Dlatego płatny pakiet chronimy **naszym** kluczem, wydawanym przy sprzedaży, w 100% pod naszą kontrolą (rywal klucza nie dostanie). Mocniejsze i prostsze niż wiązanie się z wewnętrznym mechanizmem producenta.
- **Tier darmowy bez locka terytorialnego** — przeciek angielskiej wersji na obcy rynek to darmowy marketing, nie zagrożenie.

**Otwarte (do zamknięcia w etapie):**
- Skład pakietu (funkcje, nie zawód) — do przemyślenia z Tomaszem.
- Projekt systemu kluczy: node-lock offline vs jednorazowa aktywacja online przez `ai.gstarcad.pl`.

### Etap 6 — Retencja i rozszerzenie międzynarodowe

**Status: oczekuje.**

**Cel:** utrzymać klienta przy najnowszej wersji i przygotować wejście na rynek niemiecki.

- **Dźwignia retencji: konieczność aktualizacji.** Darmowe narzędzia (i pakiet premium) wspierają **tylko najnowszą bieżącą wersję GstarCAD**. To najprostszy, najuczciwszy sposób trzymania klienta w cyklu aktualizacji — prostszy niż subskrypcja doklejona do darmowych narzędzi.
- **Rozszerzenie DE:** niemieckojęzyczne wersje materiałów, strony i pakietu premium; `ai.gstarcad.de` przygotowana. TMSys ma ekskluzywność m.in. na DE.
- **Doładowania / czat / ASKAI** — pozostają zaparkowane; wracają tylko jeśli dane z rynku pokażą realny popyt (patrz niżej).

---

## Co jest zaparkowane (nie zabite)

Trzy kierunki z wersji 1.0 są świadomie odłożone. Parkujemy je, bo odwracają wygraną ramę albo otwierają front, na który nie ma ludzi — **nie dlatego, że są złe**. Wrócą, gdy narzędzia zbudują wiarygodność i pojawi się oddech.

| Kierunek | Dlaczego zaparkowany | Warunek powrotu |
|---|---|---|
| **Czat-aplikacja za żetony** (`ai.gstarcad.pl` jako okno rozmowy z modelem, doładowania Przelewy24) | Odwraca ramę „AI po naszej stronie" (0/53 pytań o AI to dowód, że rama działa); model generuje zły kod → „GstarCAD nie działa"; koszt bez sufitu, zero przychodu | Wiarygodność zbudowana narzędziami + realny, zmierzony popyt na samodzielne promptowanie |
| **Plugin ASKAI dla klienta** (czat wewnątrz GstarCAD) | Ten sam problem złego kodu, ale w rękach klienta bez naszej kontroli; znane usterki (#19 blokada wiersza poleceń, #20/#21 edycje Standard/Pro); drugi front | Jak wyżej — narzędzia najpierw. Wykonalność już mamy (PoC zaliczony) |
| **Geodezja jako pierwszy front** | ~90% zrobiona i zwalidowana, ale garstka odbiorców vs cały rynek kreślarzy; parkuje na czystej granicy po utwardzeniu `GSAI_XYZ` | Wchodzi jako trzon **płatnego pakietu premium** (etap 5), nie jako darmowy front |

---

## Kalendarz kamieni milowych

| Data | Wydarzenie | Status |
|---|---|---|
| 30 czerwca 2026 | Start projektu — repozytoria, struktura, pierwsze dokumenty | wykonane |
| 1 lipca 2026 | Światowa premiera GstarCAD 2027 (GstarSoft HQ) — start PoC ASKAI | wykonane |
| 8 lipca 2026 | Etap 0 — PoC ASKAI zaliczony (wykonalność potwierdzona, decyzja GO) | ✅ ZALICZONE |
| 16 lipca 2026 | Webinar premiery 2027 (Robert, ~200 zapisanych). **0/53 pytań o AI** — rama potwierdzona empirycznie. Zwrot modelu → wersja 2.0 planu | ✅ przełom kierunkowy |
| 24 lipca 2026 | Badanie licencji na .240 zamknięte — paid-pack = własny klucz (nie mechanizm GstarCAD) | ✅ zamknięte |
| 30 lipca 2026 | **Plan wersja 2.0 — pełne przepisanie pod nowy model** (ten dokument) | ✅ wykonane |
| lipiec–sierpień 2026 | Etapy 1–2 — biblioteka wiedzy dojrzewa, katalog narzędzi rośnie (workhorse + ciekawostki) | w toku |
| sierpień 2026 | Etap 3 — instalator do wersji end-to-end, testy zespołu na czystym Windows | oczekuje |
| **Druga połowa września 2026** | **Polska premiera GstarCAD 2027 + publiczna premiera `ai.gstarcad.pl` (pobieralnia narzędzi).** Jeden komunikat prasowy, kampania startuje | KLUCZOWA DATA |
| jesień 2026 | Etap 5 — projekt i wydanie płatnego pakietu premium + własny klucz aktywacyjny | oczekuje |
| przełom 2026/2027 | Etap 6 — retencja przez aktualizacje; przygotowanie wersji DE | oczekuje |
| 2027 | Uruchomienie wersji niemieckiej `ai.gstarcad.de` | oczekuje |

Daty są wewnętrznym kompasem, nie obietnicą publiczną. Publicznie nie komunikujemy dat.

## Aktualizacja statusu — 30 lipca 2026

- **Model przestawiony na 2.0** — wszystkie kluczowe dokumenty (ten plan, README, PRZECZYTAJ-NAJPIERW, materiały strategiczne dla prezesów, plan marketingowy) doprowadzone do zgodności z pivotem: darmowe narzędzia = produkt/magnes, jeden płatny pakiet przez własny klucz, AI = narracja, czat/ASKAI/doładowania = zaparkowane.
- **Etap 2 — trzon workhorse gotowy, ciekawostki dochodzą.** `GSAI_ORNAMENT` (generator, panel checkboxów, każdy przebieg inny), `GSAI_SLONCE`, `GSAI_POLNOC`/`GSAI_PODZIALKA` zbudowane i przekazane zespołowi do testów. `GSAI_MEBLE` = klocek (auto-meblowanie zaparkowane jako projekt na tydzień — obserwacje zachowania odpowiednika YQArch zapisane wewnętrznie).
- **Etap 3 — instalator: brak wersji end-to-end.** Komponenty rozpoznane empirycznie (cichy Python, Zestaw Startowy przez rejestr, `.cuix` generowany), ale nie złożone w jeden przebieg i nie przetestowane na czystym Windows. To najbliższa twarda robota po katalogu narzędzi.
- **Etap 1 — biblioteka wiedzy żywa.** Referencja API rośnie z każdym narzędziem, warstwa 🟢 zwalidowana na LC, rejestr zakazanych wzorców (BUG-06/07/10) z alternatywami.
- **Dokumentacja e-CAD RO** przeniesiona do własnego repozytorium git (`init3-sentry/ecad-ro-dokumentacja`), z pełnym planem dokumentacji; stanowisko zrzutów = jego podetap.

## Co stoi obok planu

Plan obejmuje rok pracy. W tym czasie pojawią się rzeczy nieprzewidywalne dziś: nowe modele AI (Anthropic ~dwa duże rocznie), nowe wersje GstarCAD (jedna duża rocznie, latem), zmiany w prawie (RODO, KSeF, regulacje AI UE). Plan ma być nasz, nie ich.

Jeśli pojawi się model AI znacząco lepszy w generowaniu kodu Pythona — świadomie zmieniamy silnik produkcji narzędzi (Claude proaktywnie przypomina o przeglądzie co kwartał; decyzja Dawida). Jeśli GstarCAD 2027 zmieni interfejs programistyczny — aktualizujemy bibliotekę wiedzy. Jeśli konkurent w tym segmencie doda natywnego Pythona (np. BricsCAD) — przyspieszamy katalog narzędzi, żeby utrzymać przewagę pierwszego ruchu.

Plan jest aktualizowany przy każdej istotnej zmianie kierunku, każdorazowo jako **pełne przepisanie** z nową datą i osobnym zatwierdzeniem w repozytorium z czytelnym opisem powodu zmiany.

---

*Wersja 2.0 — 30 lipca 2026 (pełne przepisanie pod model: darmowe narzędzia = produkt/magnes, jeden płatny pakiet premium przez własny klucz, AI = narracja, czat/ASKAI/doładowania = zaparkowane). Poprzednia wersja 1.0 (30 czerwca 2026) w historii repozytorium. Kolejna planowana rewizja: po premierze wrześniowej — gdy pierwsze dane z rynku (pobrania narzędzi, sprzedaż licencji, aktywacje pakietu premium) pozwolą zweryfikować założenia ekonomiczne.*
