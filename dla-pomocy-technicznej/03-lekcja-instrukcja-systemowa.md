# Lekcja trzecia — Instrukcja systemowa, czyli nasz przewodnik o pygcad

Czas pracy: dwie godziny (godzina lektury, godzina ćwiczeń)

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

## Trzecie ćwiczenie praktyczne

**Zadanie A.** Otwórz pomocnika „GstarCAD Python Helper" w ChatGPT Team. Wpisz dokładnie polecenie z przykładu czwartego z lekcji drugiej (kompletne polecenie z czterema składnikami). Przeczytaj odpowiedź. Zwróć uwagę:

1. Czy używa modułów `pygcad.core` i `pygcad.pygrx`?
2. Czy ma dekorator `@command`?
3. Czy komentarze są po polsku?
4. Czy wygląda na kod, który zadziała?

Zapisz odpowiedź do pliku tekstowego `cwiczenie-03A.txt`.

**Zadanie B.** Załaduj ten skrypt do GstarCAD 2026 na swojej maszynie poleceniem `APPLOAD`. Wpisz w command line nazwę komendy. Zobacz co się stało. Zapisz w pliku tekstowym `cwiczenie-03B.txt` opis sytuacji — czy komenda się załadowała, czy działa, jeśli nie działa to dlaczego.

**Zadanie C.** Porównaj odpowiedź pomocnika z odpowiedzią „nagiego" ChatGPT-a, którą zapisałeś w lekcji pierwszej. Zwróć uwagę na różnice. Zapisz krótką notatkę w pliku `cwiczenie-03C.txt` — co konkretnie zmienia się dzięki instrukcji systemowej.

## Pytania do przemyślenia

1. Czy mogłbyś skonstruować własną instrukcję systemową — na przykład „pomocnik do pisania ofert handlowych dla klientów GstarCAD"? Co by w niej było?
2. Jakie są ograniczenia instrukcji systemowej? Czy są pytania, na które nawet pomocnik z instrukcją odpowie źle?
3. Jeśli sprzedalibyśmy GstarCAD do biura projektowego, które potrzebuje skryptów do bardzo specyficznej domeny (na przykład projektowanie kanalizacji deszczowej według polskich norm) — czy moglibyśmy stworzyć dla nich własną wyspecjalizowaną instrukcję systemową?

## Co dalej

W lekcji czwartej dowiesz się, co robić, kiedy odpowiedź modelu nie jest idealna — jak rozmawiać z nim dalej, żeby doszło do dobrego rezultatu. To jest najważniejsza lekcja w całym pakiecie, bo nawet najlepszy pomocnik z najlepszą instrukcją systemową czasem się myli, i sztuka iteracji oddziela kogoś, kto profesjonalnie pracuje z modelem językowym, od kogoś, kto się z nim szarpie.

---

*Ostatnia aktualizacja: 30 czerwca 2026*
