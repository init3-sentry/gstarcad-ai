# Wprowadzenie do projektu gstarcad-ai

Drogi Jakubie, drogi Tomaszu, drogi Rafale,

Włączam Was — formalnie, jako PM produktu GstarCAD nationwide w TMSys — do projektu, który będzie miał istotne znaczenie dla naszej firmy w nadchodzących latach. Projekt nazywa się **gstarcad-ai**. Jego celem jest uczynienie GstarCAD-a najbardziej rozpoznawalnym systemem projektowym komputerowo wspomaganym, który jako pierwszy w Polsce buduje produkcyjne wsparcie sztucznej inteligencji dla swoich klientów. Innymi słowy — chcemy żeby kiedy projektant CAD myśli „chciałbym zautomatyzować to zadanie", jego pierwszą myślą był GstarCAD, a nie konkurencyjny program.

W tym dokumencie wyjaśniam, dlaczego ten projekt jest ważny dla firmy, jakiej roli oczekuję od Was, ile czasu to zajmie, i — co dla mnie istotne — co Wy z tego osobiście wyniesiecie w wymiarze rozwoju zawodowego.

## Dlaczego to robimy

Sześćdziesiąt tysięcy aktywnych klientów GstarCAD-a w Polsce to baza, którą zbudowaliśmy przez ostatnie szesnaście lat. Ale rynek się zmienia. W ciągu ostatnich dwóch lat sztuczna inteligencja przestała być modnym hasłem, a stała się realnym narzędziem, którego coraz większa grupa projektantów używa codziennie. ChatGPT, Claude, Gemini — to są dziś nazwy znane każdemu specjaliście pod czterdziesty rok życia w branży inżynierskiej.

Nasz konkurent ZWCAD prowadzi od roku 2025 agresywną wojnę cenową. Nie wygramy z nim wyłącznie cennikiem. Musimy mieć argument, który jest realnie po naszej stronie i którego nie da się skopiować — bo wymaga decyzji architektonicznej, którą ZWCAD musiałby podjąć rok wcześniej. Tym argumentem jest **natywne wsparcie Pythona w GstarCAD 2026**.

Z sześciu głównych systemów CAD na polskim rynku — AutoCAD, AutoCAD LT, BricsCAD, ZWCAD, ARES, GstarCAD — tylko GstarCAD pozwala napisać krótki skrypt w Pythonie i załadować go jednym poleceniem `APPLOAD`, po czym skrypt natychmiast staje się nową komendą CAD. Bez programisty, bez kompilowania, bez nakładek. Skrypt może wygenerować każdy projektant, który potrafi powiedzieć modelowi językowemu (ChatGPT, Claude — obojętne) co chciałby osiągnąć. To jest realny przełom dla naszej branży i z perspektywy klienta wygląda jak magia. Naszym zadaniem jest zrobić wszystko, żeby ta magia działała perfekcyjnie u każdego naszego klienta, i żeby było o niej głośno w branży.

## Czego konkretnie potrzebuję od Was

Trzech rzeczy.

**Pierwsza — Wasza wiedza o klientach i o GstarCAD-zie.** Każdy z Was rozmawia codziennie z dziesiątkami klientów, słuchacie ich pytań, wiecie co ich boli i co by zautomatyzowali, gdyby tylko mogli. Ta wiedza jest kluczowa, żeby produkty, które zbudujemy, były naprawdę użyteczne, a nie tylko ładnie wyglądające.

**Druga — Wasze ręce do napisania pierwszych wzorcowych skryptów Pythona dla GstarCAD-a.** Każdy z Was napisze co najmniej jeden taki skrypt samodzielnie. Te skrypty będą wzorcem, na podstawie którego klienci nauczą się rozmawiać ze sztuczną inteligencją o GstarCAD-zie. Nie martwcie się, że nie znacie jeszcze pygcad (to jest oficjalna biblioteka Pythona w GstarCAD-zie) — pakiet wprowadzający, który właśnie zaczynacie, w pełni Was do tego przygotuje, krok po kroku.

**Trzecia — Wasza weryfikacja, że to wszystko faktycznie działa.** Każdy nowy skrypt, każda nowa wersja przewodnika musi być sprawdzona empirycznie w GstarCAD 2026 na Waszych maszynach, na realnych rysunkach, w realnych scenariuszach. Bez tej weryfikacji nigdy nie będziemy mieli pewności, że to, co publikujemy, naprawdę działa u klienta. Jesteście tu naszym jedynym kontrolerem jakości.

## Ile to zajmie czasu

Realistycznie — średnio półtorej godziny dziennie, czyli siedem-osiem godzin tygodniowo, przez okres najbliższych dwunastu tygodni. Po pierwszych dwunastu tygodniach intensywność spadnie do trzech-czterech godzin tygodniowo, bo będziecie pracować już głównie nad wzbogacaniem istniejących materiałów, a nie nad budowaniem od zera.

Pamiętam, że Wasza główna praca to obsługa tysięcy klientów GstarCAD. Projekt nie ma jej zastąpić ani z nią konkurować — projekt jest świadomą inwestycją w narzędzie, które za pół roku zmniejszy ilość prostych pytań, które trafiają na Wasze biurka. Klient, który dziś dzwoni z pytaniem „jak zrobić hurtowy eksport warstw do PDF-ów", za pół roku usłyszy od Was: „proszę wejść na `ai.gstarcad.pl`, wpisać dokładnie to pytanie, dostanie Pan gotowy skrypt w ciągu minuty". Trzydzieści minut telefonu zamieni się w trzydzieści sekund.

## Co Ty z tego wyniesiesz osobiście

To jest część, na której zależy mi szczególnie, bo nie chcę żebyście traktowali ten projekt jako dodatkową robotę, którą wciska Wam PM produktu. Chcę żebyście zobaczyli w tym swoją osobistą wartość.

**Po pierwsze — staniesz się specjalistą w czymś, na co rynek pracy będzie miał popyt przez najbliższe pięć-dziesięć lat.** Wiedza, jak skutecznie pracować ze sztuczną inteligencją w środowisku inżynierskim, jest dziś rzadka i wysoko ceniona. Za rok pracy w tym projekcie będziesz mieć w portfelu konkretne doświadczenie: pisanie skryptów Python dla CAD-a, projektowanie poleceń dla modeli językowych, weryfikowanie automatycznie generowanego kodu. To są umiejętności, które na rynku pracy są warte konkretne pieniądze.

**Po drugie — będziesz miał swoje nazwisko w publicznie widocznym repozytorium na GitHubie.** Pierwsze wzorcowe skrypty, które każdy z Was napisze, będą podpisane Waszym nazwiskiem. Każdy potencjalny pracodawca, każdy klient, każdy kolega z branży, który wejdzie na nasz GitHub, zobaczy Wasze konkretne dorobek. To buduje markę osobistą, której nie da się kupić.

**Po trzecie — pojawi się możliwość prowadzenia szkoleń dla klientów TMSys w zakresie automatyzacji GstarCAD-a Pythonem.** Po pół roku doświadczenia w projekcie każdy z Was będzie miał realną wiedzę, którą można przekazać. Szkolenia są dodatkowym strumieniem dochodu (wewnętrznym w TMSys) i jednocześnie buduje rozpoznawalność w branży.

**Po czwarte — bez ograniczeń, w godzinach pracy, dostęp do najnowszych narzędzi sztucznej inteligencji w wersji firmowej.** ChatGPT Team na koncie TMSys to dwadzieścia pięć dolarów miesięcznie na osobę, które nie zawsze chcielibyście wydawać prywatnie. Tu macie to dostępne.

I po piąte — najbardziej osobiste — **macie szansę być pierwszą trójką w polskiej branży CAD, która zbudowała coś takiego od podstaw**. Za rok ten projekt będzie cytowany w branżowych publikacjach. Wasze nazwiska będą tam wymienione. To rzadka okazja w karierze zawodowej i jako Wasz przełożony chcę, żebyście wykorzystali ją do końca.

## Jak będziemy pracować

W cyklach tygodniowych. Każdy z Was poświęca średnio półtorej godziny dziennie. Każdy ma swój własny tor zadań — nie czekamy na siebie, każdy idzie do przodu swoim tempem. Co piątek rano automatyczna procedura nadzorcza przegląda postęp w całym repozytorium i zapisuje raport. Raport jest jawny — każdy z Was może zobaczyć, kto co zrobił, kto utknął, kto pcha do przodu. To nie jest narzędzie do oceniania. To narzędzie do dyscyplinowania samych siebie i do pokazywania światu, że projekt naprawdę żyje.

Wraz z Wami w projekcie jest **Robert Nowakowski** — zewnętrzny stały współpracownik TMSys, prowadzący firmę szkoleniową, organizator szkoleń wyjazdowych dla naszych klientów, autor podcastów „Rysując w CAD". Ponad dwadzieścia lat doświadczenia w branży, codzienne rozmowy z projektantami i architektami. Jego rola w zespole jest inna niż Wasza — Robert jest konsultantem produktu, testerem rozwiązań i twórcą treści (webinary, podcasty). Nie zostawia codziennego wsparcia klientów, bo to właśnie do niego ich kierujemy na szkolenia. Jego pomysły na komendy będą prawdopodobnie najbardziej życiowe spośród wszystkich, bo zawodowo zajmuje się odpowiadaniem na pytanie „czego projektant naprawdę potrzebuje". Traktujcie go jak doświadczonego starszego brata zawodowego.

Komunikujemy się głównie przez komentarze do zadań w GitHubie (zaproszenia do organizacji wyślę osobno) plus krótkie cotygodniowe spotkania ze mną. Pojawienie się problemu, którego nie umiecie sami rozwiązać, jest oczekiwane — to znak, że pracujemy na granicy nowego, a nie wykonujemy rutynę. Pytajcie wcześnie, nie odkładajcie tygodnia z myślą „sam ogarnę".

## Co teraz

Przeczytajcie po kolei pięć następujących plików:

1. [`01-lekcja-czym-jest-llm.md`](01-lekcja-czym-jest-llm.md) — lekcja pierwsza
2. [`02-lekcja-jak-pisac-polecenia.md`](02-lekcja-jak-pisac-polecenia.md) — lekcja druga
3. [`03-lekcja-instrukcja-systemowa.md`](03-lekcja-instrukcja-systemowa.md) — lekcja trzecia
4. [`04-lekcja-iteracja.md`](04-lekcja-iteracja.md) — lekcja czwarta
5. [`05-lekcja-jak-sprawdzac-kod.md`](05-lekcja-jak-sprawdzac-kod.md) — lekcja piąta

Każda lekcja jest na około półtorej godziny pracy. Możecie je rozłożyć na cały tydzień po dwie godziny dziennie albo zrobić w trzy długie sesje. Polecam tempo dwie godziny dziennie przez pięć dni roboczych — daje to przestrzeń na przemyślenie i przyswojenie.

Po przejściu pięciu lekcji odbędzie się nasze spotkanie startowe, gdzie odbiorę wszystkie pytania i formalnie przekażę Wam pierwsze konkretne zadanie — napisanie własnego pierwszego skryptu Pythona dla GstarCAD-a.

Jeśli coś z tego dokumentu nie jest jasne — piszcie do mnie bezpośrednio.

Pozdrawiam,
**Dawid Jakubowski**
PM produktu GstarCAD nationwide
TMSys

---

*Wersja: 1.0 — 30 czerwca 2026*
