# Lekcja czwarta — Iteracja, czyli „nie pierwsza próba"

Czas pracy: dwie godziny (lektura plus dwa ćwiczenia praktyczne)

## Wprowadzenie

To jest najważniejsza lekcja w całym pakiecie. Po przejściu poprzednich trzech umiecie sformułować dobrze polecenie i wybrać właściwego pomocnika. Ale nawet z najlepszym poleceniem i najlepszym pomocnikiem czasem dostajecie odpowiedź, która jest „prawie dobra, ale". Sztuka iteracji — czyli rozmawiania dalej, aż dojdziecie do tego, co naprawdę potrzebujecie — jest tym, co oddziela profesjonalistę od amatora w pracy z modelem językowym.

Profesjonalista dostaje sensowny kod w dwóch-trzech turach. Amator szarpie się z piętnastoma turami i ostatecznie pisze sam. Po tej lekcji będziecie po stronie profesjonalistów.

## Co robić, kiedy odpowiedź jest „prawie dobra"

Wyobraź sobie, że dostałeś od pomocnika kod, który robi prawie to, czego potrzebujesz, ale z jednym problemem. Na przykład: kod rysuje prostokąt, ale w niewłaściwym miejscu. Albo: rejestruje komendę, ale nazwa jest po angielsku zamiast po polsku. Albo: używa funkcji `gcadGetReal()` zamiast `gcedGetReal()` (drobny błąd literowy).

Nie warto wtedy formułować całego polecenia od początku. Wystarczy odpisać pomocnikowi konkretnie, co poprawić. Reguła jest prosta: **pochwal to, co dobrze, wskaż konkretnie co źle, podaj kierunek poprawy**. Trzy zdania.

Przykład. Pomocnik dał Ci kod, w którym wszystko jest dobrze poza tym, że nazwa komendy jest `DRAW_RECTANGLE` zamiast `RYSUJ_PROSTOKAT`. Twoja odpowiedź:

> „Dobrze, kod wygląda kompletnie. Jedyna rzecz do zmiany — nazwa komendy. Zmień `DRAW_RECTANGLE` na `RYSUJ_PROSTOKAT` i zwróć cały kod ponownie."

Pomocnik odpowie poprawionym kodem w jednej iteracji. To jest profesjonalna praca.

## Cztery typowe sytuacje wymagające iteracji

Z naszego doświadczenia z modelami językowymi w środowisku CAD najczęściej spotyka się następujące cztery problemy:

**Sytuacja pierwsza — model użył nieistniejącej funkcji.** Pomocnik z instrukcją systemową robi to rzadko, ale czasem się zdarza, że wymyśli funkcję typu `pygcad.pygrx.GcDbLine.setStartPointXYZ()`, której nie ma w prawdziwym pygcad. Wtedy odpowiedz:

> „Funkcja `setStartPointXYZ` nie istnieje w pygcad. Sprawdź w referencji jakiej funkcji właściwie powinno się użyć do ustawienia punktu początkowego linii i popraw kod."

Model przeszuka swoją wiedzę kontekstową, znajdzie odpowiednik (na przykład konstruktor `GcDbLine(start_pt, end_pt)`) i poprawi.

**Sytuacja druga — model zignorował jedno z Twoich wymagań.** Powiedziałeś żeby komentarze były po polsku, a model napisał je po angielsku. Albo powiedziałeś, że nie ma używać zewnętrznych bibliotek, a użył numpy. Wtedy:

> „Zauważyłem, że komentarze są po angielsku. Powtarzam: komentarze mają być po pięknym polskim. Zwróć cały kod ponownie z polskimi komentarzami."

Drobna zniecierpliwiona uwaga („zauważyłem", „powtarzam") w żaden sposób nie pogarsza jakości odpowiedzi — model nie ma uczuć — ale jasno wskazuje, że to było wymaganie, a nie sugestia.

**Sytuacja trzecia — model zrobił coś więcej niż chciałeś.** Powiedziałeś żeby zrobił prostokąt, a on zrobił całe pomieszczenie ze ścianami, oknami, drzwiami i opisem. Wtedy:

> „Za dużo. Zostań przy samym prostokącie, bez ścian, okien, drzwi ani opisu. Wycofaj się do najprostszej wersji komendy, która rysuje sam prostokąt o podanych wymiarach."

To jest powszechny problem zwłaszcza w nowych modelach — chcą udowodnić swoją wartość pokazując więcej niż było pytane. Trzeba je krócić.

**Sytuacja czwarta — kod się ładuje, ale przy uruchomieniu wyrzuca błąd.** To jest najbardziej praktyczna sytuacja. Skopiowałeś kod do `.py`, załadowałeś przez `APPLOAD`, wpisałeś nazwę komendy w command line, dostałeś komunikat błędu w GstarCAD-zie. Wtedy:

> „Komenda się załadowała, ale przy uruchomieniu daje błąd: `[tu wkleisz dokładny tekst błędu z command line GstarCAD-a]`. Popraw kod tak, żeby ten błąd nie występował."

Wklejenie dokładnego tekstu błędu to klucz. Model używa go jako wskazówki, gdzie leży problem. Nie tłumacz swoimi słowami „coś nie działa" — daj surowy tekst.

## Jak zatrzymać iterację, kiedy nic z niej nie wychodzi

Czasem zdarza się, że iterujesz trzy, cztery razy, a każda kolejna wersja jest gorsza. Model wpada w pętlę, próbuje różnych rzeczy, miesza wzorce z różnych domen. Wtedy najlepiej nie iterować dalej.

Reguła kciuka: **jeśli po trzech iteracjach kod nie działa, zacznij od nowa w nowym chacie**. Sformułuj polecenie inaczej, z innym akcentem. Nowy chat oznacza, że model nie pamięta poprzednich nieudanych prób i podchodzi do problemu świeżo.

Czasem też się okazuje, że konkretne zadanie po prostu jest poza możliwościami pomocnika z aktualną instrukcją systemową — bo dotyka rzadkiego rogu pygcad, którego nie ma w naszym przewodniku. Wtedy zgłoś to do mnie albo do Claude'a — to znak, że trzeba uzupełnić przewodnik o dany temat. Tak rośnie nasza biblioteka wiedzy.

## Pułapka, w którą warto nie wpadać

Spotkasz się z pokusą — zamiast iterować, „pomóc" modelowi, podając mu od razu fragment kodu, który Twoim zdaniem ma być w odpowiedzi. To wydaje się efektywne, ale działa odwrotnie. Model traktuje Twój fragment jako prawdę i zaczyna budować wokół niego — nawet jeśli Twój fragment był po prostu zmyślony.

Lepsza strategia — opisać efekt, do którego dążysz, językiem naturalnym, i pozwolić modelowi znaleźć sposób. Jeśli Twój fragment jest błędny, model i tak zaadaptuje go bez krytyki. Model nie wie, że jesteś zwykłym praktykantem — traktuje Twoje słowa jak słowa eksperta. Stąd ostrożność w „podpowiadaniu".

## Czwarte ćwiczenie praktyczne

**Zadanie A.** Otwórz pomocnika „GstarCAD Python Helper". Wpisz polecenie:

> „Napisz komendę dla GstarCAD-a, która rysuje pięć równoległych poziomych linii w odstępach metra od siebie."

Przeczytaj odpowiedź. Następnie zatestuj iterację — odpowiedz pomocnikowi:

> „Zmień to. Pięć linii ma być pionowych, nie poziomych. Odstęp ma być pół metra, nie metra. Komenda ma się nazywać PIĘĆ_PIONOWYCH_LINII."

Zwróć uwagę, czy w nowej wersji wszystkie trzy zmiany zostały uwzględnione. Jeśli nie — kontynuuj iterację.

**Zadanie B.** Skopiuj końcową wersję kodu do pliku `cwiczenie-04B.py`. Załaduj do GstarCAD 2026 przez `APPLOAD`. Uruchom komendę `PIĘĆ_PIONOWYCH_LINII`. Sprawdź czy rysuje pięć pionowych linii w odstępach pół metra. Jeśli daje błąd — wklej tekst błędu z powrotem do pomocnika i kontynuuj iterację, aż zadziała.

Zapisz dziennik iteracji do pliku `cwiczenie-04-dziennik.txt` — każda kolejna wymiana między Tobą a modelem.

## Pytania do przemyślenia

1. W jakich sytuacjach iterowanie jest lepsze niż zaczynanie od nowa?
2. Jakiego rodzaju błędy widzieliście w odpowiedziach modelu najczęściej? Czy są wzorce?
3. Wyobraź sobie, że klient TMSys siedzi przy `ai.gstarcad.pl` i nie jest zadowolony z pierwszej odpowiedzi. Czy będzie sam iterował, czy zrezygnuje? Co możemy zrobić, żeby pierwsza odpowiedź była lepsza?

## Co dalej

Ostatnia lekcja — jak sprawdzać kod, który dostałeś, zanim przekażesz go klientowi albo zanim sam go uruchomisz na ważnym rysunku. Bo nawet kod, który wygląda poprawnie, może mieć subtelne problemy.

---

*Ostatnia aktualizacja: 30 czerwca 2026*
