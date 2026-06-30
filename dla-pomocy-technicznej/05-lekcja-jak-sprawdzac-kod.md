# Lekcja piąta — Jak sprawdzać kod przed jego użyciem

Czas pracy: dwie godziny (lektura plus praktyka)

## Wprowadzenie

Doszliście do ostatniej lekcji. W poprzednich czterech nauczyliście się jak rozmawiać z modelem językowym i jak dochodzić do dobrej odpowiedzi. Teraz zostaje sprawdzenie tej odpowiedzi przed użyciem — krok, który dzieli kompetentnego specjalistę od kogoś, kto przekazuje klientowi kod „na ślepo".

Pamiętajcie, że wy w tym projekcie pełnicie rolę ostatniej linii kontroli jakości. Wszystko co publikujemy publicznie — w bibliotece skryptów, w pakiecie wprowadzającym, w naszej stronie `ai.gstarcad.pl` — musi przejść przez Wasze ręce i otrzymać Wasz aprobatywny znak. Nieadekwatnie sprawdzony kod, który nie zadziała u klienta, podważa wiarygodność całego projektu.

## Co konkretnie sprawdzać

Sprawdzanie kodu Pythona dla GstarCAD-a ma sześć poziomów. Idziemy od najprostszych do najgłębszych.

**Poziom pierwszy — wzrokowy.** Czy kod używa modułów, których spodziewamy się? Czy ma dekorator `@command`? Czy komentarze są po polsku? Czy nie zawiera importu zewnętrznych bibliotek (numpy, pandas)? To są rzeczy, które widać w piętnaście sekund.

**Poziom drugi — składniowy.** Czy kod jest poprawny pod względem syntaktyki Pythona? Otwórz plik w edytorze tekstu (na przykład VS Code albo Notepad++), który podkreśla błędy składni. Jeśli zobaczysz czerwone podkreślenia, kod nie zadziała w ogóle — nawet się nie załaduje.

**Poziom trzeci — załadowanie.** Otwórz GstarCAD 2026, wpisz polecenie `APPLOAD`, wybierz plik. Powinieneś dostać komunikat „skrypt załadowany pomyślnie". Jeśli nie — Python coś źle interpretował i pokaże informację o błędzie w konsoli GstarCAD-a. Skopiuj tę informację, ona jest cennym wskaźnikiem do iteracji.

**Poziom czwarty — uruchomienie na pustym rysunku.** Załaduj komendę i wpisz jej nazwę w command line GstarCAD-a, mając otwarty nowy, pusty rysunek. Komenda powinna wykonać zadanie i nie wyrzucić błędu. Pusty rysunek jest najprostszym warunkiem testowym — wiele komend działa tu, a wywala się na pełnym rysunku.

**Poziom piąty — uruchomienie na rysunku testowym.** W folderze `materialy-testowe/` w repozytorium są przygotowane przeze mnie cztery wzorcowe rysunki: prosty rysunek mieszkania, rysunek instalacji wodno-kanalizacyjnej, rysunek skomplikowanego rzutu architektonicznego, rysunek z błędami strukturalnymi (do testów komend audytujących). Komenda powinna działać na wszystkich czterech, albo dawać sensowny komunikat błędu, jeśli rysunek ją zaskakuje.

**Poziom szósty — uruchomienie na rysunku klienta.** Ostatni poziom, którego nie zawsze możemy wykonać — załadowanie komendy na realnym rysunku jednego z klientów TMSys (oczywiście za jego zgodą). Jeśli mamy taką możliwość, korzystamy. To jest najbardziej wiarygodny test, bo realne rysunki klientów mają dziwactwa, których syntetyczne rysunki testowe nie mają.

## Najczęstsze problemy, na które warto zwracać uwagę

W naszej dotychczasowej pracy z modelami spotkaliśmy się z następującymi powtarzającymi się sytuacjami. Warto je znać, żeby wyłapać je z głowy.

**Problem pierwszy — komenda działa na pustym rysunku, ale wyrzuca błąd na pełnym.** Najczęściej znaczy to, że komenda iteruje po wszystkich obiektach rysunku, ale nie sprawdza ich typu — na przykład próbuje wywołać metodę charakterystyczną dla linii na obiekcie typu okrąg. Rozwiązanie — pytaj model żeby dodał sprawdzanie typu obiektu przed jego obrabianiem (`if isinstance(obj, GcDbLine): ...`).

**Problem drugi — kod używa nazw warstw zapisanych po polsku, ale GstarCAD nie znajduje takich warstw.** Często znaczy to, że klient ma warstwy nazwane w innej konwencji (na przykład „A-WALL" według amerykańskiej normy AIA). Komenda powinna być parametryczna — pozwalać użytkownikowi podać nazwę warstwy w command line, a nie zakładać konkretną.

**Problem trzeci — komenda działa, ale powoli na dużym rysunku.** Klient z rysunkiem trzydzieści tysięcy obiektów czeka pięć minut zamiast pół sekundy. Najczęściej to oznacza, że komenda iteruje po wszystkich obiektach zamiast użyć szybszych mechanizmów wbudowanych (zapytanie do bazy danych rysunku). Wtedy warto wrócić do pomocnika i poprosić o optymalizację.

**Problem czwarty — komenda działa, ale po jej wykonaniu rysunek wygląda dziwnie.** Na przykład komenda rysująca prostokąt rysuje go w warstwie aktywnej, a klient oczekiwał konkretnej warstwy. Albo komenda używa koloru aktualnego, a klient oczekiwał konkretnego koloru. Niedoprecyzowanie. Wracaj do pomocnika z konkretem.

**Problem piąty — komenda działa, ale klient nie wie jak ją uruchomić.** Komenda została zarejestrowana pod skomplikowaną nazwą typu `EXPORT_LAYERS_TO_PDF_WITH_NUMERATION_AND_OUTLINE`. Klient nie zapamięta tego. Dobre komendy mają zwięzłe, polskie nazwy — `WARSTWY_DO_PDF` jest lepsze niż angielska oryginał.

## Mała tablica kontrolna do każdej komendy

Przed publikacją komendy w bibliotece sprawdź każdy z tych punktów. Jeśli choć jeden nie jest spełniony — komenda jeszcze nie jest gotowa.

- [ ] Kod używa modułów `pygcad.core` i `pygcad.pygrx`
- [ ] Kod nie importuje zewnętrznych bibliotek poza standardową biblioteką Pythona
- [ ] Każda funkcja ma krótki polski komentarz mówiący, co robi
- [ ] Komenda jest rejestrowana dekoratorem `@command`
- [ ] Nazwa komendy jest po polsku albo łatwa do zapamiętania
- [ ] Komenda została załadowana w GstarCAD 2026 i nie wyrzuciła błędu przy ładowaniu
- [ ] Komenda została uruchomiona na pustym rysunku — działa
- [ ] Komenda została uruchomiona na co najmniej jednym rysunku testowym — działa
- [ ] Komenda obsługuje błędy w sposób przyjazny dla klienta (nie wywala GstarCAD-a)
- [ ] Komenda ma w komentarzu na początku pliku krótki opis tego, co robi, plus przykładowy sposób użycia
- [ ] Plik komendy ma nazwę adekwatną do jej funkcji (na przykład `eksport_warstw_do_pdf.py`)
- [ ] W folderze obok pliku komendy znajdują się dwa zrzuty ekranu pokazujące działanie

## Piąte ćwiczenie praktyczne

**Zadanie A.** Wróć do kodu, który napisałeś w ćwiczeniach poprzednich lekcji (najlepiej do końcowej wersji z ćwiczenia czwartego B). Przejdź przez tablicę kontrolną. Zaznacz, które punkty są spełnione, a które nie. Jeśli któryś nie jest — wróć do pomocnika i popraw.

**Zadanie B.** Otwórz plik `cwiczenie-04B.py`. Otwórz go też w edytorze tekstowym z podkreślaniem składni (VS Code albo inny). Jeśli są podkreślenia czerwone — popraw. Jeśli są ostrzeżenia — przemyśl, czy warto je usuwać.

**Zadanie C.** Załaduj komendę do GstarCAD-a 2026 na rysunku testowym `materialy-testowe/rysunek-mieszkania.dwg`. Uruchom. Sprawdź czy rysuje pięć pionowych linii. Zrób zrzut ekranu przed uruchomieniem komendy i po uruchomieniu. Zapisz oba zrzuty do swojego katalogu zadania.

## Co znaczy „gotowe do publikacji"

Komenda, która przeszła Twoją tablicę kontrolną i otrzymała Twój aprobatywny znak (w postaci komentarza w komitcie typu „[Twoje imię]: zweryfikowane, gotowe do publikacji"), trafia do mojego ostatniego sprawdzenia. Jeśli ja też dam zielone światło — komenda zostaje opublikowana w bibliotece skryptów, w aplikacji `ai.gstarcad.pl` jako wzorzec, oraz w katalogu `skrypty-mistrzowskie/`. Z Twoim podpisem.

## Końcowy komentarz

Doszliście do końca pakietu wprowadzającego. W ciągu dziesięciu godzin lektury i ćwiczeń dostaliście podstawę wszystkiego, co potrzebne, żeby wejść w projekt z otwartymi oczami. Następny krok to spotkanie startowe, gdzie odbiorę Wasze pytania i przekażę formalnie pierwsze konkretne zadania.

Pamiętajcie — żadne pytanie nie jest głupie. Jeśli coś z któregoś rozdziału nie jest jasne, piszcie. Jeśli macie pomysł, jak ulepszyć tę lekcję — piszcie. Ten pakiet jest dokumentem żywym i będzie się rozwijał razem z projektem.

Powodzenia.

Dawid

---

*Ostatnia aktualizacja: 30 czerwca 2026*
