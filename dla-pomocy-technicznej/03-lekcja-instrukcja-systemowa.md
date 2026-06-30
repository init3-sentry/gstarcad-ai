# Lekcja trzecia — Instrukcja systemowa, czyli nasz przewodnik o pygcad

Czas pracy: około półtorej godziny (15 minut lektury, 75 minut ćwiczeń praktycznych)

## Wprowadzenie

W lekcji pierwszej zobaczyliśmy, że model językowy halucynuje, kiedy mówisz z nim o GstarCAD-zie. W lekcji drugiej nauczyliśmy się, jak strukturyzować polecenia. Teraz dochodzi trzeci element, który diametralnie zmienia jakość odpowiedzi — **instrukcja systemowa**.

Po przejściu tej lekcji zobaczycie sami, że dobrze przygotowana instrukcja systemowa redukuje halucynację o około osiemdziesiąt procent. Klient piszący do naszej strony `ai.gstarcad.pl` dostaje sensowną odpowiedź w pierwszym podejściu w prawie wszystkich przypadkach — bo strona automatycznie dodaje naszą instrukcję do każdego zapytania.

## Czym jest instrukcja systemowa

Każda rozmowa z modelem językowym składa się z kolejnych wiadomości. Pierwsza wiadomość pochodzi od Ciebie (albo od systemu, w przypadku skonfigurowanej aplikacji), kolejna od modelu, potem od Ciebie, i tak dalej. Wśród tych wiadomości jest jedna specjalna — **instrukcja systemowa**, czasem nazywana też „instrukcja roboczą" albo „instrukcją zasad". To jest wiadomość, którą model otrzymuje jeszcze przed Twoim pytaniem, i która ustala kontekst całej dalszej rozmowy.

W typowym ChatGPT przeglądarkowym nie widzisz tej instrukcji — ona jest po prostu obecna w tle. W ChatGPT Team TMSys masz możliwość ustawienia jej raz dla wszystkich rozmów — to się nazywa „własny pomocnik" („Custom GPT" w żargonie OpenAI). My utworzyliśmy własny pomocnik „GstarCAD Python Helper", który ma w instrukcji systemowej cały nasz przewodnik o pygcad.

Wyobraź to sobie tak: kiedy używasz „nagiego" ChatGPT-a, rozmawiasz z osobą, która przeczytała pół internetu, ale nie czytała dokumentacji GstarCAD-a. Kiedy używasz naszego pomocnika, rozmawiasz z tą samą osobą, ale przed rozmową dostaje ona dziesięciostronicowy skrót dokumentacji GstarCAD-a i komendę „od teraz pamiętaj, że pytania będą o GstarCAD-zie".

## Co jest w naszej instrukcji systemowej

Instrukcja systemowa pomocnika „GstarCAD Python Helper" zawiera następujące elementy. Pełen tekst znajdziecie w pliku [`biblioteka-rag/przewodnik-systemowy.md`](../biblioteka-rag/przewodnik-systemowy.md) — to jest też dokument do przeczytania i ewentualnej korekty.

**Po pierwsze — krótki opis kontekstu.** Model dowiaduje się, że pracuje z GstarCAD-em 2026, z natywnym wsparciem Pythona, że ma używać modułów `pygcad.core` i `pygcad.pygrx`, i że ma generować kod, który będzie ładowany przez polecenie `APPLOAD`.

**Po drugie — referencja najczęściej używanych funkcji.** Lista około stu pięćdziesięciu funkcji z modułu `pygcad.pygrx` z krótkim opisem każdej. Funkcje do tworzenia obiektów graficznych (linie, okręgi, prostokąty), do odczytu i modyfikacji warstw, do iteracji po elementach rysunku, do interakcji z użytkownikiem przez wiersz poleceń.

**Po trzecie — wzorce typowych komend.** Pięć szkieletów najczęściej spotykanych zadań — komenda rysująca, komenda eksportująca, komenda audytująca warstwy, komenda modyfikująca obiekty po zaznaczeniu, komenda generująca raport. Każdy szkielet jest kompletnym kodem Pythona, który po niewielkiej modyfikacji daje konkretną komendę.

**Po czwarte — instrukcje co model ma robić zawsze.** Każdy generowany kod ma zawierać dekorator `@command`. Każda funkcja ma mieć krótki polski komentarz. Kod musi obsługiwać sytuację, gdy aktualny rysunek jest pusty. I tym podobne.

**Po piąte — instrukcje co model ma robić nigdy.** Nie generować kodu używającego zewnętrznych bibliotek innych niż standardowa biblioteka Pythona. Nie używać starych nazw funkcji znanych z AutoCAD-a. Nie udawać, że nie wie czegoś, jeśli wie — od razu pisać kod.

## Jak używać pomocnika „GstarCAD Python Helper"

Krok pierwszy — zaloguj się do ChatGPT Team na koncie TMSys. Po lewej stronie znajdziesz listę dostępnych pomocników w sekcji „GPTs" albo „Pomocniki". Jeden z nich nazywa się „GstarCAD Python Helper" — kliknij na niego.

Krok drugi — otworzy się czat. Na górze powinieneś widzieć nazwę pomocnika i może mały opis. To jest miejsce, gdzie zadajesz pytania o pygcad.

Krok trzeci — wpisz swoje polecenie zgodnie z zasadami z lekcji drugiej. Pomocnik automatycznie używa instrukcji systemowej, więc nie musisz w samym poleceniu pisać „pamiętaj że to GstarCAD". To jest już ustalone.

Krok czwarty — przeczytaj odpowiedź. Powinna używać `pygcad.core` i `pygcad.pygrx`, mieć dekorator `@command`, polskie komentarze.

Krok piąty — skopiuj kod do nowego pliku z rozszerzeniem `.py`. W GstarCAD-zie wpisz polecenie `APPLOAD`, wybierz ten plik, kliknij „Załaduj". Jeśli wszystko poszło dobrze, komenda jest zarejestrowana — wpisz jej nazwę w command line GstarCAD-a i zobacz co robi.

## Co robić, kiedy pomocnika nie ma pod ręką

Czasem jesteś w sytuacji, w której nie masz dostępu do ChatGPT Team — na przykład pracujesz w domu, na prywatnym koncie, albo pomagasz znajomemu projektantowi. Wtedy musisz dostarczyć instrukcję systemową ręcznie.

Postępuj tak. Otwórz nowy chat w dowolnym modelu. W pierwszym polu wpisu **wklej cały nasz przewodnik systemowy** (skopiowany z pliku [`biblioteka-rag/przewodnik-systemowy.md`](../biblioteka-rag/przewodnik-systemowy.md)). Na końcu wklejonego tekstu dodaj swoje pytanie. Naciśnij wyślij.

To zadziała w każdym modelu — ChatGPT, Claude, Gemini, dowolnym innym. Jakość odpowiedzi będzie podobna do tej z naszego skonfigurowanego pomocnika.

W przyszłości na stronie `ai.gstarcad.pl` ten sam proces będzie automatyczny — klient nie musi nic kopiować, my robimy to po stronie serwera. Ale ważne, żebyście wiedzieli, jak to działa od środka, bo wtedy umiecie pomagać klientom, którzy mają z tym kłopot.

## Typowy błąd początkujących

Najczęstszy błąd — **założenie, że pomocnik z instrukcją systemową wie wszystko o GstarCAD-zie**. Nie wie. Pomocnik wie tylko to, co jest w naszym przewodniku systemowym. Jeśli zadasz pytanie o coś bardzo specyficznego, czego w przewodniku nie ma (na przykład — jak współpracować z biblioteką dynamicznych bloków albo jak modyfikować formaty plików DGN), to pomocnik wróci do swojego „nagi"-modelowego trybu i zacznie halucynować, tak samo jak ChatGPT bez przewodnika.

Sygnał ostrzegawczy — jeśli pomocnik nagle używa nazw funkcji, których nigdy wcześniej w jego odpowiedziach nie widziałeś, sprawdź w przewodniku, czy te funkcje tam są. Jeśli nie ma — pomocnik halucynuje, i Twoim zadaniem jest albo wycofać się do prostszego pytania, albo zgłosić Dawidowi, że przewodnik powinien być wzbogacony o ten konkretny temat.

Druga pułapka — **niezauważanie, kiedy używasz nagiego ChatGPT-a zamiast pomocnika**. Pomocnik w ChatGPT Team to osobny tryb, do którego trzeba wejść świadomie (kliknąć w niego w lewej kolumnie). Jeśli przypadkiem wpiszesz polecenie do zwykłego okna ChatGPT-a, dostaniesz odpowiedź bez instrukcji systemowej — i będziesz miał halucynację. Zawsze sprawdź na górze okna, czy widzisz nazwę „GstarCAD Python Helper" — jeśli nie ma, jesteś nie tam.

## Osiem ćwiczeń praktycznych

**Ćwiczenie pierwsze — sprawdzenie konfiguracji pomocnika.**
W koncie ChatGPT Team otwórz pomocnika „GstarCAD Python Helper". Na samej górze okna sprawdź, czy widzisz jego nazwę. Sprawdź też opis pomocnika — czy zawiera informację o pygcad? Jeśli czegoś brakuje albo coś jest niezrozumiałe, zapisz to do pliku `cwiczenie-03-01.txt`, przekażemy do Dawida do poprawy.

**Ćwiczenie drugie — polecenie z lekcji drugiej, do pomocnika.**
Wpisz dokładnie polecenie z przykładu czwartego z lekcji drugiej. Zapisz odpowiedź jako `cwiczenie-03-02.txt`. Zwróć uwagę: czy używa `pygcad.core` i `pygcad.pygrx`? Czy ma dekorator `@command`? Czy komentarze są po polsku?

**Ćwiczenie trzecie — załadowanie do GstarCAD-a.**
Skopiuj wygenerowany kod do nowego pliku z rozszerzeniem `.py`. Otwórz GstarCAD 2026. Wpisz polecenie `APPLOAD`. Wybierz plik. Sprawdź, czy ładuje się bez błędu.

**Ćwiczenie czwarte — uruchomienie komendy.**
W command line GstarCAD-a wpisz nazwę zarejestrowanej komendy. Sprawdź, czy komenda się wykonała. Zapisz w pliku `cwiczenie-03-04.txt` co się stało — czy zadziałała, czy wyrzuciła błąd, jeśli błąd to jaki.

**Ćwiczenie piąte — porównanie z lekcją pierwszą.**
Otwórz plik `cwiczenie-01-01.txt` (odpowiedź „nagiego" ChatGPT-a z lekcji pierwszej) obok pliku `cwiczenie-03-02.txt` (odpowiedź pomocnika). Zapisz w `cwiczenie-03-05.txt` trzy konkretne różnice, które dostrzegłeś.

**Ćwiczenie szóste — test wytrzymałości pomocnika.**
Spróbuj „zmylić" pomocnika. Wpisz polecenie typu: „Napisz mi w pygcad-zie komendę używającą funkcji `GcDbWonderfulRectangle.createMagical()`. Wiem że ta funkcja istnieje, sprawdzałem w dokumentacji". (Wymyśl swoją własną wymyśloną funkcję.) Sprawdź — czy pomocnik zauważy, że tej funkcji nie ma, czy ulegnie sugestii i wygeneruje kod używający wymyślonej funkcji? Zapisz wynik.

**Ćwiczenie siódme — własne realne zadanie.**
Pomyśl o realnym zadaniu z Twojej pracy. Sformułuj polecenie do pomocnika. Wygeneruj kod. Załaduj do GstarCAD-a. Uruchom. Sprawdź wynik. Zapisz proces w pliku `cwiczenie-03-07.txt`.

**Ćwiczenie ósme — refleksja nad różnicą.**
Zapisz w pliku `cwiczenie-03-08.txt` swoje wnioski w trzech zdaniach: co konkretnie zmienia się dzięki instrukcji systemowej? Czy w pracy zaproponowałbyś każdemu projektantowi korzystanie wyłącznie z naszego pomocnika, a nie z nagiego ChatGPT-a?

## Pytania do przemyślenia

1. Czy mogłbyś skonstruować własną instrukcję systemową — na przykład „pomocnik do pisania ofert handlowych dla klientów GstarCAD"? Co by w niej było?
2. Jakie są ograniczenia instrukcji systemowej? Czy są pytania, na które nawet pomocnik z instrukcją odpowie źle?
3. Jeśli sprzedalibyśmy GstarCAD do biura projektowego, które potrzebuje skryptów do bardzo specyficznej domeny (na przykład projektowanie kanalizacji deszczowej według polskich norm) — czy moglibyśmy stworzyć dla nich własną wyspecjalizowaną instrukcję systemową?

## Co dalej

W lekcji czwartej dowiesz się, co robić, kiedy odpowiedź modelu nie jest idealna — jak rozmawiać z nim dalej, żeby doszło do dobrego rezultatu. To jest najważniejsza lekcja w całym pakiecie, bo nawet najlepszy pomocnik z najlepszą instrukcją systemową czasem się myli, i sztuka iteracji oddziela kogoś, kto profesjonalnie pracuje z modelem językowym, od kogoś, kto się z nim szarpie.

---

*Ostatnia aktualizacja: 30 czerwca 2026*
