# Mapa drogowa projektu gstarcad-ai

Wersja: 1.0 — 30 czerwca 2026 (pierwsza wersja przy starcie projektu).
Autor: Dawid Jakubowski (PM produktu GstarCAD nationwide, TMSys) + Claude (Anthropic).

Dokument jest naszym wewnętrznym kompasem strategicznym. Pokazuje co, kiedy i w jakiej kolejności robimy. Zmieniany jest świadomie i z datą — żeby było widać, kiedy coś się przesunęło i dlaczego. Każda kolejna wersja jest pełnym przepisaniem z aktualną datą.

## Cele projektu

Krótko: **uczynić GstarCAD-a najbardziej rozpoznawalnym systemem CAD w segmencie cenowym, który jako pierwszy w Polsce buduje produkcyjne wsparcie sztucznej inteligencji dla swoich klientów**. Z tego celu wynikają cztery konkretne mierzalne wskaźniki sukcesu, do których będziemy dążyć:

1. **Pozyskanie nowych klientów.** Co najmniej dwustu projektantów CAD spoza dotychczasowej bazy TMSys ma w ciągu pierwszych dwunastu miesięcy działania projektu skontaktować się z TMSys w sprawie zakupu licencji GstarCAD, z pierwotnym źródłem informacji w postaci naszej strony `ai.gstarcad.pl`, kanału tematycznego na portalach branżowych lub treści wideo opublikowanych w ramach projektu.
2. **Pozycja w dyskusji branżowej.** GstarCAD ma być rozpoznawalnie wymieniany jako system z natywnym Pythonem i ze wsparciem sztucznej inteligencji w co najmniej pięciu znaczących publikacjach branżowych (portale, blogi, materiały wideo niezależnych projektantów) w ciągu pierwszego roku istnienia projektu.
3. **Aktywacja istniejących klientów.** Co najmniej dwa tysiące unikalnych klientów GstarCAD z bazy TMSys ma w ciągu pierwszego roku zalogować się na `ai.gstarcad.pl` ze swoim numerem licencji co najmniej trzykrotnie. To wskaźnik realnej, powtarzalnej wartości produktu.
4. **Samofinansowanie.** Po dwunastu miesiącach od uruchomienia funkcji doładowań (planowane Q4 2026) projekt ma generować comiesięczny przychód co najmniej równy comiesięcznym kosztom infrastruktury i interfejsu programistycznego Anthropic. Wpływy z doładowań mają pokrywać sto procent kosztów bieżącej działalności.

Pierwszy i drugi cel są priorytetowe (per decyzja strategiczna Dawida z czerwca 2026). Trzeci jest naturalną konsekwencją pierwszego. Czwarty jest miarą zdrowia finansowego projektu w dłuższej perspektywie.

## Etapy projektu — perspektywa półroczna

Praca podzielona jest na cztery etapy. Każdy etap ma konkretną datę zakończenia i konkretne wymierne kryteria zaliczenia. Etapy nie są równe długością — krótsze są bardziej intensywne, dłuższe pozwalają na pracę o niskim, ale stałym tempie.

### Etap pierwszy — Biblioteka wiedzy o pygcad dla sztucznej inteligencji

**Czas trwania:** od 1 lipca 2026 do 31 lipca 2026 (cztery tygodnie).

**Cel etapu:** doprowadzić do stanu, w którym dowolny projektant CAD wpisuje w okno czatu modelu sztucznej inteligencji (ChatGPT, Claude, Gemini, dowolny inny) krótkie zapytanie typu „napisz mi komendę GstarCAD-a w Pythonie, która eksportuje wszystkie warstwy bieżącego rysunku do osobnych plików PDF", a w odpowiedzi otrzymuje gotowy plik z rozszerzeniem `.py`, który po załadowaniu poleceniem `APPLOAD` w GstarCAD-zie 2026 natychmiast działa, bez konieczności poprawiania kodu.

**Mierzalne kryteria zaliczenia etapu:**

- Plik [`biblioteka-rag/przewodnik-systemowy.md`](biblioteka-rag/przewodnik-systemowy.md) zawiera kompletną referencję najczęściej używanych funkcji modułów `pygcad.core` i `pygcad.pygrx` (co najmniej sto pięćdziesiąt funkcji, czyli najpopularniejsza piątka procent z około siedmiuset dziewięćdziesięciu dostępnych w pełnej dokumentacji producenta).
- Folder [`biblioteka-rag/przyklady/`](biblioteka-rag/przyklady/) zawiera co najmniej dwadzieścia działających skryptów `.py`, każdy z komentarzem opisującym co robi i każdy przetestowany empirycznie w GstarCAD 2026 przez Dawida albo przez zespół pomocy technicznej.
- Przewodnik systemowy został opublikowany jako Niestandardowy GPT w sklepie OpenAI pod nazwą roboczą „GstarCAD Python Helper", widoczny publicznie.
- Ten sam przewodnik został opublikowany jako projekt w aplikacji Claude pod tą samą nazwą, widoczny publicznie.
- Co najmniej dziesięciu klientów TMSys spoza zespołu projektowego przetestowało publicznie dostępnego pomocnika i przesłało potwierdzenie, że wygenerowane skrypty działają w ich GstarCAD-zie 2026.
- Pierwszy tekst blogowy o projekcie, w pięknym polskim, opublikowany na blogu TMSys (`tmsys.pl/blog`) — z odnośnikami do pomocnika i do tego repozytorium.
- Krótki film dziewięćdziesięciu-sekundowy pokazujący cały przepływ (zapytanie do modelu, otrzymany skrypt, załadowanie do GstarCAD-a, działająca komenda) opublikowany na koncie YouTube TMSys.

### Etap drugi — Aplikacja internetowa ai.gstarcad.pl

**Czas trwania:** od 1 sierpnia 2026 do 31 sierpnia 2026 (cztery tygodnie).

**Cel etapu:** uruchomić publiczną stronę pod adresem `ai.gstarcad.pl`, na której każdy klient TMSys może w prosty sposób wygenerować dla siebie skrypt Pythona dla GstarCAD-a, bez konieczności samodzielnego promptowania modelu i bez konieczności posiadania własnej subskrypcji jakiegokolwiek narzędzia sztucznej inteligencji.

**Mierzalne kryteria zaliczenia etapu:**

- Domena `ai.gstarcad.pl` jest aktywna i prowadzi do działającej aplikacji.
- **Aplikacja ma nowoczesny interfejs typu chat** — nie formularz. Klient widzi okno rozmowy z modelem, wpisuje polecenie, obserwuje odpowiedź modelu w czasie rzeczywistym linia po linii (streaming). W ramach tej samej rozmowy może dopisać kolejne polecenia typu „popraw kolor na niebieski", „dodaj obsługę pustego rysunku" — historia rozmowy widoczna. To wzorzec, którego klient AI 2026 się spodziewa (ChatGPT, Claude, Cursor). Formularz stron internetowych sprzed pięciu lat by go rozczarował.
- Aplikacja korzysta z modelu Sonnet 5 firmy Anthropic, klucz programistyczny zakupiony przez TMSys z zabezpieczonym limitem miesięcznym dwustu dolarów na start.
- Strona ma trzy warstwy dostępu: anonimową (do trzech zapytań na dobę, do dwóch tysięcy pięciuset żetonów na odpowiedź), z adresem pocztowym (do pięciu zapytań na dobę, do sześciu tysięcy żetonów) i z numerem licencji GstarCAD weryfikowanym w bazie TMSys (do dziesięciu zapytań na dobę, do dwunastu tysięcy żetonów).
- Wszystkie zabezpieczenia przed nadużyciem są wdrożone: Cloudflare Turnstile (test odróżnienia człowieka od bota), limit na adres internetowy, sztywna struktura polecenia po stronie serwera, twarde ograniczenie liczby żetonów odpowiedzi, próg powiadomienia o przekroczeniu stu dolarów miesięcznie, próg blokady przy dwustu dolarach.
- Regulamin sprzedaży i klauzula informacyjna o ochronie danych osobowych są zatwierdzone przez prawnika TMSys i opublikowane na stronie.
- Aplikacja zapisuje dziennik zapytań w bazie SQLite, do której dostęp ma wyłącznie Dawid oraz wskazani administratorzy.
- Strona jest dostępna w pełnej polskiej polszczyźnie, bez wstawek anglojęzycznych, w tonie spójnym z resztą materiałów projektu.
- Czas oczekiwania na odpowiedź (od naciśnięcia przycisku przez klienta do pojawienia się gotowego pliku do pobrania) wynosi nie więcej niż dwadzieścia sekund w typowym scenariuszu.
- Pierwsze stu klientów testowych (zaproszonych spośród bazy TMSys) skorzystało z aplikacji i przesłało potwierdzenie poprawnego działania.

### Etap trzeci — Galeria mistrzowska i biblioteka gotowych komend

**Czas trwania:** od 1 września 2026 do 30 listopada 2026 (dwanaście tygodni).

**Cel etapu:** stworzyć katalog najwyższej jakości gotowych skryptów Pythona dla GstarCAD-a, które klient może pobrać bezpośrednio z biblioteki i używać. To są skrypty, które są zbyt duże, zbyt rozbudowane albo wymagają zbyt wielu warstw funkcjonalności, żeby model sztucznej inteligencji generował je z każdego zapytania od nowa. Tworzymy je raz, ręcznie, dopieszczamy do perfekcji, dokumentujemy. Klient nie generuje takiego skryptu — on go zaciąga.

**Etap trzeci jest też naturalnym momentem na poszerzenie zespołu o piątą osobę** — Robert Nowakowski ma zaprzyjaźnionego kolegę-programistę z porównywalnym do niego dwudziestoletnim stażem CAD-owym, ale z głębokim doświadczeniem programowania nakładek (.NET, ObjectARX, LISP). Jego perspektywa programisty CAD da pomysły na skrypty mistrzowskie, których ani chłopcy z pomocy, ani Robert szkoleniowiec by nie wymyślili. Wdrożenie tej osoby do projektu prowadzi Robert (Dawid nie ma bezpośredniego kontaktu), nazwisko i szczegóły uzupełniamy w miarę pojawiania się informacji.

**Mierzalne kryteria zaliczenia etapu:**

- Folder [`skrypty-mistrzowskie/`](skrypty-mistrzowskie/) zawiera co najmniej pięćdziesiąt różnych komend, każda z osobnym katalogiem, w katalogu co najmniej cztery pliki: kod źródłowy `.py`, polski przewodnik użytkownika, dwa zrzuty ekranu pokazujące działanie, plik testowy (rysunek DWG) na którym komenda działa.
- Katalog jest dostępny przez interfejs do pobrania pakietów programowych Pythona (komenda `pip install gstarcad-power-tools`), pakiet jest opublikowany w publicznym rejestrze pakietów Pythona (PyPI) pod marką „GstarCAD Power Tools by TMSys".
- Plik [`skrypty-mistrzowskie/README.md`](skrypty-mistrzowskie/) prezentuje kompletną listę skryptów z krótkim opisem każdego, w pięknej polszczyźnie.
- Dla pięciu najatrakcyjniejszych skryptów (kreator klatki schodowej, generator zestawienia materiałowego, audyt zgodności z normą, kreator BIM-lite, narzędzie do porównania dwóch wersji rysunku) są przygotowane krótkie filmy wideo (do dwóch minut każdy) opublikowane na koncie YouTube TMSys.
- Co najmniej tysiąc unikalnych klientów TMSys pobrało biblioteczkę w ciągu pierwszych dwóch miesięcy od jej publikacji.

### Etap 3.5 — Plugin ASKAI dla GstarCAD

**Czas trwania:** od 1 grudnia 2026 do 31 grudnia 2026 (cztery tygodnie).

**Cel etapu:** dostarczenie klientom natywnego doświadczenia sztucznej inteligencji **wewnątrz GstarCAD-a**, bez konieczności wychodzenia do przeglądarki. Krytyczne dla realnego wrażenia „AI wbudowana w mój CAD", które jest tym, czego klient docelowy (a szczególnie decydent techniczny i CIO korporacji) się dziś spodziewa.

Klient wpisuje w wiersz poleceń GstarCAD-a nową komendę `ASKAI`. Otwiera się okno dialogowe z chatem. Wpisuje polecenie po polsku, obserwuje strumień odpowiedzi modelu w czasie rzeczywistym, klika przycisk „Wykonaj tutaj" — wygenerowany skrypt ładuje się automatycznie do bieżącego rysunku, bez wychodzenia z okna GstarCAD-a i bez ręcznego `APPLOAD`. Kolejne polecenia w tej samej sesji, jeśli klient chce.

**Mierzalne kryteria zaliczenia etapu:**

- Plugin w Pythonie rejestrujący komendę `ASKAI` przez dekorator `@command` z modułu `pygcad.core`.
- Okno dialogowe z chat-style interface napisane w bibliotece `tkinter` (standardowa biblioteka Pythona, cross-Windows-kompatybilna, nie wymaga dodatkowych zależności u klienta).
- Streaming odpowiedzi modelu z zaplecza `ai.gstarcad.pl` — klient widzi kod generowany na żywo, tak samo jak w oknie strony webowej.
- Przycisk „Wykonaj tutaj" wykonujący wygenerowany skrypt bezpośrednio w bieżącym rysunku — funkcja automatycznego ładowania kodu bez konieczności zapisu do pliku.
- Autoryzacja poprzez numer licencji GstarCAD — te same limity dziennych zapytań co przez stronę webową (dziesięć zapytań na dobę dla klienta z licencją, po dwanaście tysięcy żetonów każde).
- Test u co najmniej pięciu klientów pilotażowych — dwa biura projektowe (obecni klienci TMSys), dwaj indywidualni projektanci, jedna korporacja z bazy pięćdziesięciu największych (kandydat na pilotaż korporacyjny).
- Instrukcja instalacji dla klientów końcowych w pięknym polskim — jeden krótki film oraz jednostronicowy przewodnik pisemny.
- Publikacja pluginu jako pakietu do pobrania ze sklepu TMSys — darmowo dla wszystkich klientów z aktywną licencją GstarCAD.

**Znaczenie strategiczne etapu:** Ten plugin realnie odróżnia GstarCAD od konkurencji. AutoCAD nie ma niczego takiego (i długo mieć nie będzie — Autodesk pracuje w innym rytmie). ZWCAD nie ma natywnego Pythona, więc nie da rady zbudować takiego mechanizmu. BricsCAD wymagałby konfiguracji, której klient nie chce robić. **Konfiguracji GstarCAD + Plugin ASKAI + zaplecze AI nie da się skopiować bez roku dedykowanej pracy przez konkurenta.** Plus — dla korporacji ten plugin to konkretny obiekt, który CIO pokazuje zarządowi jako „nasze wdrożenie AI w warsztacie projektowym". Nie strona internetowa gdzieś tam. Coś, co widzą projektanci co dzień w swoim narzędziu pracy.

### Etap czwarty — Doładowania, konkurs i rozszerzenie międzynarodowe

**Czas trwania:** od 1 stycznia 2027 do 30 czerwca 2027 (sześć miesięcy).

**Cel etapu:** uruchomić mechanizm doładowań (umożliwiający klientom przekraczanie dziennych limitów za niewielką opłatą), uruchomić cotygodniowy konkurs „skrypt tygodnia" jako narzędzie marketingu treści, oraz przygotować strukturalną i językową infrastrukturę pod rozszerzenie projektu na rynek niemiecki w roku 2027.

**Mierzalne kryteria zaliczenia etapu:**

- Mechanizm doładowań przez Przelewy24 jest zintegrowany ze sklepem TMSys. Klient kupuje pakiet (od pięciu do czterystu złotych) tak samo jak licencję GstarCAD, dostaje fakturę.
- Pakiet roczny doładowań dla klientów z licencją GstarCAD daje dodatkową zniżkę piętnaście procent na odnowienie licencji w przyszłym roku. Mechanizm jest opisany w regulaminie sklepu TMSys i widoczny dla klienta przy zakupie.
- Cotygodniowy konkurs „skrypt tygodnia" jest uruchomiony — każdy piątek wybieramy jedno zapytanie z bazy, generujemy odpowiedź z pełną mocą modelu (do dwudziestu tysięcy żetonów odpowiedzi), publikujemy wynik w galerii pod nazwiskiem autora zapytania (za jego zgodą), autor dostaje upominek (roczna darmowa subskrypcja GstarCAD Standard albo materiały firmowe).
- Niemieckojęzyczna wersja przewodnika systemowego dla sztucznej inteligencji, regulamin sprzedaży, klauzula informacyjna i interfejs strony są przygotowane i sprawdzone przez kompetentnego korektora. Adres `ai.gstarcad.de` jest przygotowany do uruchomienia.
- Klient niemiecki ma w pierwszej połowie 2027 roku możliwość skorzystać z aplikacji w taki sam sposób jak klient polski.
- Projekt do końca trzeciego kwartału 2027 osiąga samofinansowanie (suma comiesięcznych wpływów z doładowań przekracza sumę comiesięcznych kosztów infrastruktury i interfejsu programistycznego Anthropic).

## Kalendarz kamieni milowych

| Data | Wydarzenie | Status |
|---|---|---|
| 30 czerwca 2026 | Start projektu — repozytoria utworzone, struktura folderów, pierwsze dokumenty | wykonane |
| 7 lipca 2026 | Pierwsze wersje wszystkich kluczowych dokumentów (instrukcja systemowa, pakiet dla chłopaków, streszczenie dla prezesów, plan marketingowy, mechanizm nadzoru) | oczekuje |
| 14 lipca 2026 | Pierwsze formalne włączenie zespołu pomocy technicznej (Jakub, Tomasz, Rafał) do projektu | oczekuje |
| 31 lipca 2026 | Etap pierwszy zakończony | oczekuje |
| 31 sierpnia 2026 | Etap drugi zakończony — aplikacja `ai.gstarcad.pl` działa publicznie | oczekuje |
| 1 września 2026 | Pierwsza kampania marketingowa skierowana do projektantów spoza bazy TMSys | oczekuje |
| 30 listopada 2026 | Etap trzeci zakończony — galeria pięćdziesięciu skryptów | oczekuje |
| 31 grudnia 2026 | Etap 3.5 zakończony — plugin ASKAI dla GstarCAD wydany dla klientów | oczekuje |
| 1 stycznia 2027 | Uruchomienie doładowań i konkursu tygodnia | oczekuje |
| 1 stycznia 2027 | Pierwsza wewnętrzna ocena dwunastomiesięczna projektu | oczekuje |
| 1 marca 2027 | Uruchomienie wersji niemieckiej `ai.gstarcad.de` | oczekuje |
| 30 czerwca 2027 | Projekt osiąga samofinansowanie | oczekuje |

## Co stoi obok planu

Plan obejmuje pełen rok pracy. W tym czasie pojawią się rzeczy, których nie da się dziś przewidzieć: nowe modele sztucznej inteligencji (Anthropic wydaje średnio dwa duże modele rocznie, OpenAI podobnie, Google podobnie), nowe wersje GstarCAD-a (rocznie jedna duża wersja, latem), zmiany w prawie polskim (RODO, e-faktury KSeF, dyrektywy unijne dotyczące sztucznej inteligencji), zmiany w naszej własnej organizacji. Plan ma być nasz, nie ich. To znaczy, że jeśli pojawi się model sztucznej inteligencji o trzy razy lepszej jakości generowania kodu Pythona za połowę ceny, świadomie zmieniamy konfigurację aplikacji — to jest udokumentowane jako stały mechanizm (Claude proaktywnie przypomina o aktualizacji silnika co kwartał).

Jeśli pojawi się GstarCAD 2027 z ważną zmianą w interfejsie programistycznym, automatycznie aktualizujemy przewodnik systemowy. Jeśli pojawi się nowy konkurent z podobną funkcjonalnością w innej linii produktowej (na przykład BricsCAD doda natywne wsparcie Pythona) — przyspieszamy etapy trzeci i czwarty, żeby utrzymać przewagę pierwszego ruchu na rynku.

Plan jest aktualizowany przy każdej istotnej zmianie kierunku. Każda aktualizacja jest osobnym zatwierdzeniem zmian w repozytorium z czytelnym opisem powodu zmiany.

---

*Pierwsza wersja planu: 30 czerwca 2026. Kolejna planowana rewizja: początek października 2026 (po zakończeniu etapu drugiego, w trakcie etapu trzeciego — moment, w którym pierwsze dane z aplikacji `ai.gstarcad.pl` pozwolą zweryfikować założenia ekonomiczne).*
