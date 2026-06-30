# Przeczytaj najpierw

Witaj w projekcie **gstarcad-ai**. Ten dokument jest pierwszą rzeczą, którą warto przeczytać po wejściu do repozytorium. Wyjaśnia o co w tym wszystkim chodzi, dla kogo jest ten projekt, kto za nim stoi i jak się w niego włączyć.

## O co chodzi

GstarCAD 2026 to system projektowy komputerowy wspomagający (oprogramowanie typu CAD — *Computer-Aided Design*) używany przez ponad sześćdziesiąt tysięcy projektantów w Polsce: w biurach architektonicznych, instalacyjnych, drogowych, geodezyjnych, mechanicznych i wielu innych. Jest to produkt firmy GstarSoft z Chin, dystrybuowany w Polsce wyłącznie przez TMSys.

Od wersji 2026 GstarCAD oferuje pełne, natywne wsparcie języka programowania Python. Oznacza to, że projektant CAD, który chce zautomatyzować jakąś czynność — na przykład hurtową zmianę warstw w pięciuset rysunkach, automatyczne zliczenie powierzchni pomieszczeń, eksport wszystkich arkuszy do osobnych plików PDF — może napisać krótki skrypt w Pythonie i załadować go do GstarCAD-a jednym poleceniem. Skrypt natychmiast staje się nową komendą CAD, dostępną tak samo jak wbudowane polecenia typu „linia" albo „okrąg".

Spośród sześciu głównych systemów CAD na rynku polskim (AutoCAD, AutoCAD LT, BricsCAD, ZWCAD, ARES, GstarCAD) tylko GstarCAD pozwala na taką integrację bez kompilowania, bez konfigurowania zintegrowanego środowiska programistycznego, bez specjalnych nakładek. To unikalna przewaga produktowa.

**Ten projekt wykorzystuje tę przewagę.** Budujemy trzy rzeczy równocześnie.

**Po pierwsze, bazę wiedzy dla sztucznej inteligencji** (folder `biblioteka-rag`). Modele językowe takie jak ChatGPT, Claude czy Gemini, gdy pytasz je o napisanie kodu dla GstarCAD-a, generują kod, który nie działa — bo zostały nauczone na tysiącach przykładów AutoCAD-a, a o GstarCAD-zie wiedzą bardzo niewiele. Naszym zadaniem jest dostarczyć im skondensowany przewodnik o pygcad (oficjalnej bibliotece Pythona w GstarCAD), żeby z każdego zapytania generowały kod, który po załadowaniu od razu działa. Ten przewodnik staje się fundamentem wszystkiego, co dalej.

**Po drugie, aplikację internetową** dostępną pod adresem `ai.gstarcad.pl` (folder `web-app`). Klient TMSys wchodzi na stronę, opisuje co potrzebuje („potrzebuję komendy, która eksportuje wszystkie warstwy z bieżącego rysunku do osobnych plików PDF z numerami arkuszy w nazwie pliku"), naciska przycisk, a po kilkunastu sekundach otrzymuje gotowy plik z rozszerzeniem `.py`. Wgrywa go do GstarCAD-a poleceniem `APPLOAD` — i nowa komenda działa. Bez programowania, bez konfiguracji, bez nauki Pythona.

**Po trzecie, bibliotekę gotowych skryptów mistrzowskich** (folder `skrypty-mistrzowskie`). To są największe, najbardziej dopracowane skrypty, które tworzymy sami: kreatory parametrycznych elementów, narzędzia kontrolne, automaty do projektów wielkoarkuszowych. Klient pobiera je gotowe i używa.

## Dla kogo to robimy

Projekt jest skierowany przede wszystkim do **klientów docelowych**, czyli osób, które dopiero rozważają zakup systemu CAD albo które rozważają zmianę swojego obecnego systemu na inny. Naszą bronią jest pokazanie, że GstarCAD to nie jest „tańszy klon AutoCAD-a", tylko nowoczesny system, który jako jedyny w swojej klasie cenowej rozumie się ze sztuczną inteligencją bez tłumacza.

Drugą grupą są **istniejący klienci TMSys**, którzy używają GstarCAD-a od lat. Dla nich projekt jest dodatkową korzyścią z posiadania licencji — narzędziem, które oszczędza im godziny pracy tygodniowo.

Trzecią grupą są **decydenci w dużych biurach projektowych**, dla których argument „nasz CAD już potrafi pracować ze sztuczną inteligencją" jest istotny przy podejmowaniu decyzji o standaryzacji systemu w skali całego biura. Polskie biura projektowe od dziesięciu i więcej stanowisk to grupa docelowa, na którą szczególnie zwracamy uwagę.

## Kto za tym stoi

Projekt prowadzi **Dawid Jakubowski**, PM produktu GstarCAD nationwide w TMSys. W TMSys od szesnastu lat — najpierw jako sprzedawca, potem lider zespołu sprzedaży, następnie PM produktu, a od końca 2026 roku odpowiedzialny też za rozwój produktu na rynku niemieckim oraz na Litwie, Łotwie, w Estonii, na Ukrainie i w Rumunii.

W projekt zaangażowany jest zespół pomocy technicznej GstarCAD w TMSys w składzie:

- **Jakub Moszko**
- **Tomasz Gach**
- **Rafał Trzusło**

Każdy z nich poświęca na ten projekt średnio półtorej godziny dziennie, łącznie z codziennymi obowiązkami obsługi klientów GstarCAD w Polsce. Pamiętaj, że obsługa techniczna sześćdziesięciu tysięcy klientów jest ich główną pracą — projekt jest świadomą inwestycją w narzędzie, które długoterminowo zmniejszy ilość prostych pytań, które trafiają na ich biurka.

Plus do projektu na stałe dołącza **Robert Nowakowski** — zewnętrzny stały współpracownik TMSys z ponad dwudziestoletnim doświadczeniem w branży CAD. Robert prowadzi własną firmę szkoleniową, organizuje dla TMSys szkolenia wyjazdowe i nagrywa podcasty „Rysując w CAD". W projekcie jest dla nas trzykrotnym wzmocnieniem: po pierwsze, jako weteran branży i konsultant strategiczny przy projektowaniu komend (jego pomysły są bardziej życiowe niż nasze, bo dziesiątki lat rozmawia z architektami i projektantami); po drugie, jako tester nowych rozwiązań, prawdopodobnie najbardziej zaangażowany ze wszystkich; po trzecie, jako twórca treści — będzie prowadził webinary o naszym narzędziu i poświęci mu odcinki swojego podcastu.

Wsparcie merytoryczne i przygotowanie materiałów (przewodniki dla sztucznej inteligencji, plan, dokumenty dla zarządu, materiały marketingowe, mechanizm nadzoru postępu) zapewnia Claude — system sztucznej inteligencji firmy Anthropic, działający bezpośrednio przy Dawidzie w narzędziu Claude Code. W praktyce oznacza to, że niemal cała dokumentacja, plan i kod podstawowy powstają w dialogu pomiędzy Dawidem a Claude'em, a zespół pomocy technicznej dochodzi do wzbogacania, weryfikacji empirycznej w GstarCAD-zie 2026 i obsługi klientów.

## Jak się włączyć

Jeśli jesteś z zespołu pomocy technicznej TMSys i właśnie ten projekt został Ci przedstawiony przez Dawida — przejdź do folderu [`dla-pomocy-technicznej/`](dla-pomocy-technicznej/) i przeczytaj pakiet wprowadzający. Składa się z pięciu krótkich lekcji, łącznie dziewięciu-dziesięciu godzin nauki rozłożonej na jeden tydzień. Lekcje są napisane w taki sposób, że nie wymagają wcześniejszej znajomości sztucznej inteligencji ani Pythona w GstarCAD-zie — wszystko zaczynamy od podstaw. Po przeczytaniu lekcji otrzymasz dostęp do pierwszego konkretnego zadania, opisanego w folderze [`tasks/`](tasks/).

Jeśli jesteś klientem TMSys i zajrzałeś tu z ciekawości — zapraszamy do śledzenia postępu. Aplikacja, która będzie generować dla Ciebie skrypty, ruszy pod adresem [ai.gstarcad.pl](https://ai.gstarcad.pl) gdzieś w sierpniu-wrześniu 2026 roku. Jeśli chcesz wpisać się na listę powiadomień o uruchomieniu, napisz do swojego opiekuna handlowego w TMSys.

Jeśli jesteś projektantem CAD pracującym dziś na innym systemie (AutoCAD, BricsCAD, ZWCAD, ARES) i przyszedłeś tu zobaczyć, co my właściwie robimy — zachęcamy do przejrzenia folderu [`biblioteka-rag/przyklady/`](biblioteka-rag/przyklady/). Tam pokazujemy konkretne komendy Pythona, które działają w GstarCAD-zie 2026 po jednym kliknięciu. Pomyśl, ile czasu zaoszczędziłbyś w ciągu roku, gdyby Twój CAD też tak potrafił.

## Jak ten projekt jest prowadzony

Pracujemy w cyklach tygodniowych. Każdy piątek rano automatyczna procedura nadzorcza przegląda postęp w całym repozytorium i zapisuje raport do folderu [`przeglady/`](przeglady/). Raport zawiera: jakie zadania ruszyły, jakie utknęły, ocenę tempa i konkretne rekomendacje na nadchodzący tydzień. Jest jawny — każda osoba zainteresowana może go przeczytać. To narzędzie dyscyplinujące dla zespołu i element przejrzystości dla klientów.

Cała strategia, harmonogram, lista zadań, kryteria akceptacji każdego zadania są w pliku [`PLAN.md`](PLAN.md). Jeśli chcesz zobaczyć perspektywę długoterminową — zacznij od tam.

## Krótko o nazwach folderów

| Folder | Co tu znajdziesz |
|---|---|
| `tasks/` | Konkretne zadania — po jednym pliku na zadanie, oznaczone identyfikatorami T-001, T-002 i dalej |
| `przeglady/` | Cotygodniowe raporty z postępu prac, generowane w piątki rano |
| `biblioteka-rag/` | Materiały zasilające sztuczną inteligencję wiedzą o pygcad (instrukcji programistycznych GstarCAD-a) |
| `web-app/` | Kod aplikacji internetowej `ai.gstarcad.pl` |
| `dla-pomocy-technicznej/` | Pakiet wprowadzający dla zespołu wsparcia TMSys (lekcje, słowniki, instrukcje) |
| `dla-marketingu/` | Materiały do publikacji blogowej, treści społecznościowe, hasła reklamowe |
| `skrypty-mistrzowskie/` | Najlepsze, najbardziej dopracowane skrypty produkcyjne — gotowe do użytku przez klientów |

## Krótkie słowo o języku

W tym repozytorium kod programu i techniczne instrukcje obsługi narzędzi programistycznych są pisane po angielsku — to wymóg branżowy, ułatwia współpracę z międzynarodową społecznością i z modelami sztucznej inteligencji. Natomiast wszystkie dokumenty kierowane do zespołu polskiego, dokumenty wewnętrzne, materiały marketingowe i dokumentacja użytkowa dla klientów są pisane po pięknym, poprawnym, polskim. Słownik polskich odpowiedników terminów programistycznych znajdziesz w folderze `dla-pomocy-technicznej/`.

To świadoma decyzja redakcyjna i jednocześnie wyznacznik jakości. Polszczyzna w naszych dokumentach jest narzędziem budowania zaufania u polskiego klienta. Trzymamy poziom.

---

*Aktualizacja: 30 czerwca 2026 — pierwsza wersja przy starcie projektu. Plik będzie ewoluował w miarę postępu prac.*
