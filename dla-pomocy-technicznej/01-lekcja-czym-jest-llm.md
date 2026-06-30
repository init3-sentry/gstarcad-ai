# Lekcja pierwsza — Czym jest model językowy i dlaczego on kłamie

Czas pracy: około półtorej godziny (15 minut lektury, 75 minut ćwiczeń praktycznych)

## O co tu chodzi

Każdy z Was słyszał określenie „sztuczna inteligencja" tysiące razy w ostatnich dwóch latach. Większość ludzi używa go bez wnikania w to, co naprawdę za nim stoi. W tej lekcji odkładamy marketing na bok i opisujemy spokojnym językiem, jak to faktycznie działa — i co ważniejsze, dlaczego czasem działa fantastycznie, a czasem produkuje przekonująco wyglądające bzdury.

To nie jest lekcja teoretyczna z myślą o przygotowaniu Was do studiów magisterskich z informatyki. To jest lekcja praktyczna z myślą o tym, żebyście wiedzieli, kiedy ufać modelowi, kiedy mu nie ufać, i jak rozpoznać, że właśnie powiedział Wam coś, co brzmi mądrze, ale nie jest prawdą.

## Co to za zwierzę

Określenia „sztuczna inteligencja", „model językowy", „duży model językowy", „LLM" (skrót od angielskiego określenia tej samej rzeczy) — wszystkie odnoszą się do tego samego rodzaju programu komputerowego. Najpopularniejsze przykłady: ChatGPT firmy OpenAI, Claude firmy Anthropic, Gemini firmy Google. W tym projekcie będziemy używać głównie ChatGPT (w wersji „Team" zakupionej przez TMSys) i Claude'a (przez moje konto Claude Code).

Model językowy to program, który został wytrenowany — czyli nauczony — na ogromnej liczbie tekstów. Mówiąc bardzo konkretnie: cały publicznie dostępny internet, miliony książek, miliony naukowych publikacji, podręczniki techniczne, dokumentacje, fora dyskusyjne. Setki miliardów słów, w wielu językach, z wielu dziedzin. Po przeczytaniu tego wszystkiego model nauczył się jednej rzeczy — przewidywać, jakie słowo prawdopodobnie pojawi się następne, biorąc pod uwagę kontekst tego, co już zostało napisane.

Brzmi to dziwnie prosto. I jest dziwnie proste. Cała wyrafinowana zdolność modelu do prowadzenia rozmów, do tłumaczenia, do pisania kodu, do rozwiązywania zadań matematycznych sprowadza się do tej jednej umiejętności — bardzo dobrze przewiduje kolejne słowo na podstawie kontekstu.

Wyobraź sobie najbardziej oczytaną osobę na świecie, która przeczytała wszystko co kiedykolwiek napisano, ale która ma jedno ograniczenie — nie wie, co jest prawdziwe, a co nie. Wie tylko, jakie słowa zwykle pojawiają się razem. Kiedy ją pytasz „kto był pierwszym prezydentem Polski po roku 1989?", odpowiada „Lech Wałęsa", bo zna kontekst i nauczyła się, że te słowa pasują do siebie. Kiedy ją pytasz „jaki jest największy ośrodek przemysłowy w Bydgoszczy?", odpowiada coś, co brzmi przekonująco, niezależnie od tego, czy to akurat zgodne z rzeczywistością. Ona nie wie, że nie wie.

To jest klucz do zrozumienia, dlaczego model językowy bywa zawodny.

## Halucynacja — kiedy model kłamie nie wiedząc, że kłamie

Kiedy model językowy mówi coś, co nie jest prawdą, ale brzmi przekonująco — branża nazywa to „halucynacją". Jest to wprowadzające w błąd określenie, bo sugeruje świadomy proces. W rzeczywistości model nie wie, że halucynuje. On po prostu przewiduje kolejne słowa na podstawie wzorców, które widział w tekstach treningowych, a czasem wzorzec wskazuje na coś, czego w rzeczywistości nie ma.

Konkretny przykład z naszej branży. Powiedzmy, że pytasz ChatGPT: „Napisz mi komendę GstarCAD-a w Pythonie, która rysuje okrąg o promieniu pięć metrów w środku rysunku."

ChatGPT odpowiada przekonująco brzmiącym kodem:

```python
from gstarcad import application
doc = application.get_current_document()
doc.draw_circle(center=(0, 0), radius=5.0)
```

Wygląda świetnie. Brzmi profesjonalnie. Jest jeden mały problem — to nie działa. W GstarCAD-zie nie ma żadnego modułu o nazwie `gstarcad`. Nie ma funkcji `application.get_current_document()`. Nie ma metody `doc.draw_circle()`. To wszystko jest wymyślone. Model językowy nigdy nie widział faktycznej dokumentacji GstarCAD-a, ale widział tysiące dokumentacji innych systemów CAD (głównie AutoCAD-a), w których podobne wzorce się pojawiały. Wygenerował kod, który wygląda jak prawdziwy, ale którego po prostu nie ma.

Jeśli załadujesz ten kod do GstarCAD-a, dostaniesz błąd. Spokój — to nic strasznego. Po prostu kod nie zadziała.

Ale wyobraź sobie, że klient wpisał takie zapytanie na naszej stronie `ai.gstarcad.pl`, dostał taką wymyśloną odpowiedź, próbował ją załadować — i zniechęcił się. Naszym zadaniem w tym projekcie jest sprawić, żeby to się nie zdarzyło. Stąd ogromny nacisk na **przewodnik systemowy** o pygcad — instrukcja, którą wpisujemy modelowi przed każdym pytaniem klienta, żeby on wiedział, czego ma używać, a czego ma nie używać.

## Skąd halucynacja w przypadku GstarCAD-a wynika

Modele językowe trenowane są na publicznie dostępnych tekstach. AutoCAD ma ogromną ilość publicznej dokumentacji, milionów linii kodu na GitHubie, dziesiątki książek napisanych w ciągu czterech dekad. Model zna AutoCAD-a bardzo dobrze.

GstarCAD od wersji 2026 ma natywne wsparcie Pythona. Publiczna dokumentacja tej funkcjonalności w internecie jest niewielka — kilka stron na portalu producenta, jedna publikacja w postaci pliku PDF, trochę materiałów na forach. To kropla w oceanie w porównaniu z AutoCAD-em. Dlatego model nie zna pygcad i kiedy go pytasz o coś z tej dziedziny, wymyśla rzeczy na podstawie wzorców z AutoCAD-a.

Stąd nasza rola. **My piszemy ten przewodnik o pygcad, żeby model nie musiał wymyślać.** Wkładamy mu tę wiedzę do kontekstu na początku każdej rozmowy. Wtedy on wie, że ma używać `pygcad.core` i `pygcad.pygrx`, a nie wymyślonego `gstarcad`. To jest sercem tego projektu.

## Jak rozpoznać halucynację

Konkretne sygnały, na które warto zwracać uwagę przy czytaniu kodu wygenerowanego przez model:

**Pierwszy sygnał — import modułu, który dziwnie wygląda.** Jeśli widzisz `from gstarcad import ...` albo `import gcad`, albo cokolwiek innego niż `from pygcad.core import *` i `from pygcad.pygrx import *`, to prawdopodobnie halucynacja.

**Drugi sygnał — funkcja, która wygląda zbyt dobrze, żeby istniała.** Jeśli kod używa funkcji `draw_text_with_outline_and_shadow()` z dwudziestoma argumentami, to prawdopodobnie taka funkcja nie istnieje. Pygcad jest biblioteką niskopoziomową — pojedyncza funkcja robi jedną prostą rzecz.

**Trzeci sygnał — nazwy klas i metod, których nie ma w przewodniku systemowym.** Jeśli kod używa `GcDbWonderfulObject` albo `GstarCadDocument`, sprawdź w naszym przewodniku, czy taki obiekt istnieje. Jeśli nie ma — to halucynacja.

**Czwarty sygnał — odwołanie do bibliotek zewnętrznych, których klient nie ma.** Model czasem generuje kod używający bibliotek typu `numpy`, `pandas`, `pillow`. Te biblioteki mogą nie być zainstalowane w środowisku Pythona dostępnym dla GstarCAD-a. Klienta to zaskoczy. Lepiej trzymać się standardowej biblioteki Pythona.

**Piąty sygnał — kod, który wygląda na skopiowany z AutoCAD-a.** Jeśli widzisz `import win32com.client` i `acad = win32com.client.Dispatch("AutoCAD.Application")` — to definitywnie nie jest kod dla GstarCAD-a. To jest klasyczna halucynacja w naszej branży.

## Typowy błąd początkujących

Najczęstszy błąd osób, które dopiero zaczynają pracę z modelami językowymi — **wiara modelowi na słowo, bez sprawdzenia**. Łatwo dać się zwieść przekonującemu tonowi odpowiedzi. Model nie pisze „prawdopodobnie", „może", „spróbuj sprawdzić" — pisze wprost, jakby wszystko, co podaje, było zweryfikowanym faktem. To kwestia stylu, nie pewności.

Sygnał ostrzegawczy, na który warto zwracać uwagę: **jeśli odpowiedź jest podejrzanie pewna siebie, bez ani jednego „prawdopodobnie", „zazwyczaj", „w większości przypadków" — model jest najprawdopodobniej w trybie halucynacji**. Prawdziwy ekspert hedguje. Halucynujący model nie.

Druga oznaka — kiedy model używa nazw funkcji, klas albo modułów, które wyglądają „zbyt logicznie". `GcDbWonderfulRectangleWithRoundCorners` — brzmi sensownie, ale prawdopodobnie zmyślone. Im bardziej kompletna i „idealna" nazwa, tym większe ryzyko, że model ją wymyślił przed chwilą.

## Osiem ćwiczeń praktycznych

Wykonuj je po kolei, każde wymaga rzeczywistego działania, nie tylko czytania.

**Ćwiczenie pierwsze — pierwsze zapytanie do „nagiego" modelu.**
Otwórz konto ChatGPT Team TMSys (zaproszenie dostaniesz osobnym mailem). Załóż nowy chat. Wpisz dokładnie:

> „Napisz mi komendę GstarCAD-a w Pythonie, która rysuje prostokąt o wymiarach pięć na trzy metry."

Naciśnij wyślij. Przeczytaj odpowiedź. Zapisz całą odpowiedź do pliku `cwiczenie-01-01.txt`.

**Ćwiczenie drugie — analiza importów.**
W odpowiedzi z ćwiczenia pierwszego, wyróżnij wszystkie linie zaczynające się od `import` albo `from`. Zapisz je na osobnej liście. Następnie zastanów się — czy każdy z tych importów wygląda na prawdziwy moduł GstarCAD-a, czy może być wymyślony? Twoja intuicja na tym etapie wystarczy.

**Ćwiczenie trzecie — analiza nazw funkcji i klas.**
W odpowiedzi z ćwiczenia pierwszego, wyróżnij wszystkie nazwy funkcji (rzeczy zakończone nawiasami, jak `setStartPoint()`) i nazwy klas (rzeczy zaczynające się dużą literą, jak `GcDbLine`). Zapisz je na osobnej liście.

**Ćwiczenie czwarte — porównanie z prawdziwą referencją.**
Otwórz plik `biblioteka-rag/przewodnik-systemowy.md` (znajdziesz go w tym samym repozytorium). Przeszukaj go po nazwach, które wynotowałeś w ćwiczeniach drugim i trzecim. Ile z nich faktycznie tam występuje? Zapisz wynik w pliku `cwiczenie-01-04.txt` — coś w stylu „z dziewięciu zidentyfikowanych nazw, sześć występuje w przewodniku, trzy nie".

**Ćwiczenie piąte — powtarzalność halucynacji.**
W tym samym koncie ChatGPT otwórz NOWY chat (kluczowe — musi być nowy, żeby model nie pamiętał poprzedniego). Wpisz dokładnie to samo polecenie co w ćwiczeniu pierwszym. Porównaj nową odpowiedź z poprzednią. Czy są identyczne? Czy w nowej odpowiedzi pojawiły się inne nazwy funkcji?

**Ćwiczenie szóste — drugi model.**
Jeśli masz prywatne konto Claude albo Gemini, wpisz tam to samo polecenie. (Jeśli nie masz — pomiń to ćwiczenie.) Porównaj wszystkie trzy odpowiedzi: ChatGPT odpowiedź A, ChatGPT odpowiedź B, Claude/Gemini. Czy halucynują w identyczny sposób, czy każdy „wymyśla" co innego?

**Ćwiczenie siódme — własne polecenie.**
Wymyśl swoje własne zapytanie — coś z Twojej rzeczywistej pracy, czego klient TMSys mógłby Cię realnie spytać. Na przykład: „napisz komendę, która zmieni warstwę wszystkich tekstów na warstwę TEKSTY". Wpisz do ChatGPT. Powtórz analizę z ćwiczeń drugiego, trzeciego i czwartego. Zapisz wynik.

**Ćwiczenie ósme — własna lista obserwacji.**
Zapisz w pliku `cwiczenie-01-08.txt` swoje trzy największe zaskoczenia z tej lekcji. Konkrety, nie ogólniki. Na przykład: „zaskoczyło mnie, że ChatGPT za każdym razem używa innej nazwy funkcji dla tego samego zadania" albo „zaskoczyło mnie, że model używał `pyautocad`, którego nigdy w życiu nie słyszałem". Tę listę przeczytamy razem na spotkaniu startowym.

## Pytania do przemyślenia

Zanim przejdziesz do lekcji drugiej, zastanów się przez chwilę nad następującymi pytaniami:

1. Jeśli model językowy halucynuje, dlaczego w ogóle warto go używać do generowania kodu?
2. W jakich sytuacjach halucynacja modelu jest groźna dla klienta, a w jakich tylko irytująca?
3. Czy ta sama halucynacja może się powtórzyć, jeśli zadasz to samo pytanie dwa razy?

Nie musisz pisać odpowiedzi. Wystarczy że pomyślałeś.

## Co dalej

W lekcji drugiej dowiesz się, jak strukturyzować polecenia do modelu, żeby z góry zminimalizować ryzyko halucynacji — niezależnie od tego, czy używasz „nagiego" ChatGPT-a, czy naszego skonfigurowanego pomocnika.

---

*Ostatnia aktualizacja: 30 czerwca 2026*
