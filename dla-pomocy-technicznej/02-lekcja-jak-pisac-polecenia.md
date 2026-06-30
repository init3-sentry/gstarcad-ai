# Lekcja druga — Jak pisać polecenia, żeby dostać sensowną odpowiedź

Czas pracy: około półtorej godziny (15 minut lektury, 75 minut ćwiczeń praktycznych)

## Wprowadzenie

W lekcji pierwszej dowiedzieliście się, że model językowy bywa zawodny. Teraz uczymy się, jak konstruować polecenia tak, żeby ta zawodność występowała jak najrzadziej. Po przejściu tej lekcji powinniście umieć rozmawiać z modelem na takim poziomie, że dostajecie sensowny kod w jednej, może dwóch próbach — zamiast walczyć przez piętnaście prób, jak to zwykle wygląda u osób, które nie nauczyły się tej sztuki.

## Cztery elementy dobrego polecenia

Polecenie do modelu językowego ma cztery składniki. Im więcej z nich uwzględnisz, tym lepszą odpowiedź dostaniesz. Nie wszystkie cztery są zawsze konieczne, ale brak któregokolwiek z nich pogarsza jakość.

**Pierwszy składnik — kontekst.** Czyli o czym w ogóle rozmawiamy. Czy mówimy o GstarCAD-zie czy o AutoCAD-zie? Czy chodzi o wersję 2026 czy o starszą? Czy jest to skrypt jednorazowy, czy ma być powtarzalnym narzędziem? Im więcej kontekstu, tym mniejsze ryzyko halucynacji.

**Drugi składnik — zadanie.** Konkretnie, co model ma zrobić. Nie „pomóż mi z rysunkiem", tylko „napisz komendę w Pythonie, która eksportuje wszystkie warstwy bieżącego rysunku do osobnych plików PDF". Im konkretniej, tym lepiej.

**Trzeci składnik — ograniczenia.** Co model ma zrobić, a czego ma nie robić. Na przykład: „użyj wyłącznie pygcad.core i pygcad.pygrx, nie używaj zewnętrznych bibliotek". Albo: „komenda ma być rejestrowana przez dekorator @command, nie przez inny mechanizm". Ograniczenia chronią Was przed halucynacją.

**Czwarty składnik — format odpowiedzi.** Jak ma wyglądać to, co model Wam zwróci. „Tylko kod Pythona, bez wyjaśnień" albo „kod plus krótki komentarz po polsku co robi każda funkcja" — to są dwa różne formaty i model będzie traktował je inaczej.

## Pięć przykładów od najgorszego do najlepszego polecenia

Te przykłady są celowo skonstruowane tak, żeby pokazać Wam ewolucję dobrego polecenia. Wszystkie pięć dotyczy tego samego zadania — napisania komendy w Pythonie, która rysuje pomieszczenie prostokątne o zadanych wymiarach.

### Przykład pierwszy — bardzo źle

> „Narysuj pokój."

To jest klasyczne polecenie, jakie pisze osoba, która nigdy nie pracowała z modelem językowym. Brak kontekstu (gdzie? w czym?), brak konkretu (jaki pokój?), brak ograniczeń, brak formatu odpowiedzi. Model będzie zgadywał — i prawdopodobnie poda Ci coś niepasującego.

### Przykład drugi — źle

> „Napisz mi w Pythonie kod, który rysuje pokój o wymiarach pięć na cztery metry."

Trochę lepiej. Jest konkret (Python, wymiary), ale brakuje kontekstu o GstarCAD-zie i o pygcad. Model wciąż może wygenerować kod używający wymyślonej biblioteki.

### Przykład trzeci — średnio

> „Napisz mi w Pythonie komendę dla GstarCAD-a 2026, która rysuje pokój o wymiarach pięć na cztery metry."

Już dużo lepiej. Pojawia się kontekst (GstarCAD 2026), więc model zacznie szukać sensownego rozwiązania w tej domenie. Ale wciąż może próbować różnych bibliotek — może wymyślić jakąś nieistniejącą, jeśli nie pamięta pygcad.

### Przykład czwarte — dobrze

> „Napisz mi komendę dla GstarCAD-a 2026 w Pythonie używającą pygcad.core i pygcad.pygrx. Komenda ma rysować prostokąt o wymiarach pięć na cztery metry w środku rysunku (środek prostokąta w punkcie zero, zero, zero), na warstwie o nazwie POKOJE, kolorem czerwonym. Komenda ma być rejestrowana przez dekorator @command pod nazwą RYSUJ_POKOJ."

To już jest konkretne polecenie. Kontekst — GstarCAD 2026, pygcad. Zadanie — rysuje prostokąt. Konkrety — wymiary, lokalizacja, warstwa, kolor, sposób rejestracji. Model dostanie ten sam kontekst za każdym razem i prawdopodobnie odpowie sensownie.

### Przykład piąte — bardzo dobrze

> „Napisz mi komendę dla GstarCAD-a 2026 w Pythonie używającą pygcad.core i pygcad.pygrx. Komenda ma rysować prostokąt o wymiarach pięć na cztery metry w środku rysunku, na warstwie o nazwie POKOJE, kolorem czerwonym. Komenda ma być rejestrowana przez dekorator @command pod nazwą RYSUJ_POKOJ. Zwróć tylko kod Pythona w bloku kodu, bez wyjaśnień przed ani po. Kod ma zawierać krótki komentarz po polsku pod każdą funkcją mówiący co robi."

Tutaj dochodzą dwa elementy z czwartego składnika — format odpowiedzi. „Zwróć tylko kod, bez wyjaśnień" — eliminuje przedmowy modelu typu „świetnie, oto co potrzebujesz", które są bezużyteczne. „Komentarz po polsku" — wskazuje, że ma być spójne z naszą polityką językową.

## Reguła generalna

Pisz polecenia tak, jakbyś tłumaczył zadanie nowemu praktykantowi, który zaczął pracę dziś rano i nie wie jeszcze niczego o Waszej firmie ani o Waszych preferencjach. Nie zakładaj, że cokolwiek jest „oczywiste". Każde słowo, które niepowiedziane, model wymyśli sam.

To może wydawać się czasochłonne, ale wręcz odwrotnie — czas, który zaoszczędzisz na nie powtarzaniu polecenia pięć razy, znacznie przekracza czas włożony w napisanie go raz, ale dobrze.

## Typowy błąd początkujących

Najczęstszy błąd — **uprzejmość w komunikacji z modelem**. „Czy mógłbyś łaskawie", „proszę", „byłbym wdzięczny" — to są słowa, które dodają objętości poleceniu, ale nie poprawiają jego jakości. Model nie ma uczuć, nie odczuwa uznania ani urazy.

Jeszcze gorsze — niektórzy próbują „motywować" model: „to bardzo ważne dla mnie", „jestem początkujący, więc proszę o cierpliwość". Model nie reaguje na motywację. On po prostu dobiera kolejne słowo na podstawie wzorców z tekstów treningowych. Im więcej dodatkowych słów wokół właściwego zadania, tym bardziej rozmywa się intencja.

Pisz dyrektywnie — „napisz", „wygeneruj", „popraw", „zwróć". Nie obrazi się. Jakość odpowiedzi rośnie, gdy szum komunikacyjny maleje.

Druga pułapka — **lista zakazów zamiast pozytywnych wskazań**. „Nie używaj numpy, nie używaj pandas, nie używaj scipy, nie używaj win32com" — paradoksalnie zwiększa szansę, że model po którąś z tych nazw sięgnie. Lepiej: „użyj wyłącznie pygcad.core i pygcad.pygrx" — pozytywne wskazanie zawsze działa lepiej niż negacyjne.

## Osiem ćwiczeń praktycznych

Każde ćwiczenie wymaga konkretnego działania. Nie czytaj samych poleceń — wykonuj je.

**Ćwiczenie pierwsze — kontrolne, przykład czwarty.**
W koncie ChatGPT Team wpisz dokładnie polecenie z przykładu czwartego z tej lekcji (kompletne polecenie z kontekstem, zadaniem, ograniczeniami). Zapisz odpowiedź jako `cwiczenie-02-01.txt`. Zwróć uwagę, że model używa pygcad.

**Ćwiczenie drugie — kontrolne, przykład piąty.**
Otwórz nowy chat. Wpisz dokładnie polecenie z przykładu piątego (z formatem odpowiedzi). Zapisz odpowiedź jako `cwiczenie-02-02.txt`. Zwróć uwagę: czy model dostosował się do formatu? Czy faktycznie odpowiedział tylko kodem, bez przedmowy? Czy komentarze są po polsku?

**Ćwiczenie trzecie — porównanie jakości.**
Otwórz oba pliki z ćwiczeń pierwszego i drugiego obok siebie. Zapisz w pliku `cwiczenie-02-03.txt` trzy konkretne różnice, które dostrzegłeś. Nie ogólniki („drugi jest lepszy"), tylko konkrety („w pierwszym model dodał sześćset słów przedmowy, w drugim zero").

**Ćwiczenie czwarte — modyfikacja polecenia.**
Weź polecenie z przykładu piątego. Zamień w nim „prostokąt o wymiarach pięć na cztery metry" na „okrąg o promieniu dwa metry". Resztę polecenia zostaw bez zmiany. Wpisz w ChatGPT. Sprawdź, czy model trzymał format (tylko kod, polskie komentarze, dekorator `@command`). Zapisz wynik.

**Ćwiczenie piąte — polecenie skrócone.**
Weź to samo zadanie (rysowanie okręgu), ale teraz napisz polecenie używając tylko TRZECH składników (kontekst, zadanie, ograniczenia) — z pominięciem formatu odpowiedzi. Wpisz w ChatGPT. Porównaj jakość odpowiedzi z poprzednią (z ćwiczenia czwartego). Czy widzisz różnicę?

**Ćwiczenie szóste — celowo źle.**
Napisz polecenie celowo źle — jak w przykładzie pierwszym z tej lekcji („narysuj pokój"). Wpisz w ChatGPT. Sprawdź jakość odpowiedzi. To ćwiczenie ma na celu utwierdzenie Cię w przekonaniu, że konstrukcja polecenia naprawdę ma znaczenie.

**Ćwiczenie siódme — własne polecenie z realnej pracy.**
Pomyśl o sytuacji z ostatniego tygodnia, w której klient TMSys pytał Cię o automatyzację, której nie mogłeś mu od razu zaproponować. Skonstruuj polecenie do modelu według wszystkich czterech składników (kontekst, zadanie, ograniczenia, format). Wpisz. Zapisz wynik jako `cwiczenie-02-07.txt`. Oceń sam, czy odpowiedź jest na poziomie, który mógłbyś przekazać klientowi.

**Ćwiczenie ósme — refleksja.**
Zapisz w pliku `cwiczenie-02-08.txt` swoje trzy najważniejsze wnioski z tej lekcji. Jakie zachowanie zmienisz w swoich własnych poleceniach do modeli? Czy są rzeczy, które robiłeś prywatnie z ChatGPT-em źle?

## Co nie działa

Kilka błędów, które warto omijać:

**„Bądź ekspertem od GstarCAD-a, kiedy mi odpowiadasz."** Ten popularny chwyt — proszenie modelu o przyjmowanie ról — w naszym przypadku niewiele daje. Model „nie czuje się" ekspertem od GstarCAD-a, bo niewiele o nim wie. Lepsze jest konkretne dostarczenie mu wiedzy w postaci instrukcji systemowej, czego nauczymy się w lekcji trzeciej.

**„Daj mi najlepszą możliwą odpowiedź."** Model nie wie, co dla Ciebie jest „najlepsze". Lepsze jest konkretne sprecyzowanie kryteriów.

**„Przepraszam, że Cię niepokoję, ale czy mógłbyś łaskawie..."** Grzeczność jest miła w rozmowie z ludźmi, ale modelowi językowemu nie pomaga. Ona dorzuca dodatkowe słowa do polecenia, ale nie zwiększa szansy na sensowną odpowiedź. Możesz pisać do modelu wprost — nie obraża się.

**„Nie używaj numpy, nie używaj pandas, nie używaj scipy."** Lista zakazów bywa skuteczna, ale długa lista zakazów paradoksalnie zwiększa szansę, że model zacznie ich używać. Lepsza strategia — wskazać pozytywnie, czego ma używać („użyj wyłącznie pygcad.core i pygcad.pygrx"). Pozytywne wskazania działają lepiej niż negatywne.

## Pytania do przemyślenia

1. Patrząc na trzy odpowiedzi, które właśnie wygenerowałeś — która jest najlepsza i dlaczego?
2. Czy polecenie z przykładu pięć było zbyt długie? A może powinno być jeszcze dłuższe?
3. Wyobraź sobie, że klient TMSys wpisuje swoje pierwsze polecenie do naszej strony `ai.gstarcad.pl`. Jakie polecenie prawdopodobnie wpisze i jakiej jakości odpowiedzi się spodziewa?

## Co dalej

W lekcji trzeciej dochodzi nowy element — **instrukcja systemowa**, czyli stała wiedza, którą wpisujemy modelowi raz na początku rozmowy, żeby on automatycznie wiedział, że pracuje z GstarCAD-em. To zmienia jakość odpowiedzi diametralnie.

---

*Ostatnia aktualizacja: 30 czerwca 2026*
