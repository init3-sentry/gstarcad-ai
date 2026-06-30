# T-010 — Pierwsza własna komenda Roberta: trzy propozycje do wyboru

| Pole | Wartość |
|---|---|
| Identyfikator | T-010 |
| Etap | pierwszy |
| Przypisany do | **Robert Nowakowski** |
| Przewidywany czas | 8 godzin (z bardzo elastycznym terminem) |
| Status | oczekuje |
| Data wejścia | 2026-07-15 |
| Data deklarowanego ukończenia | 2026-07-31 |
| Zależy od | T-009 (Robert ukończył wprowadzenie) |

## Cel

Pierwsza własna komenda Roberta — z elementem wyboru tematu. Ponieważ Robert sam ma najlepsze wyczucie, jakie komendy będą najatrakcyjniejsze do prezentacji na jego webinarach i w jego podcastach, daje mu zostawiamy wybór jednego z trzech tematów. Każdy z nich pasuje do roli „szkoleniowo-marketingowej", którą Robert pełni w projekcie.

## Trzy propozycje tematów

**Temat pierwszy — komenda demonstracyjna na pierwsze nagranie podcastu „Rysując w CAD".**
Nazwa robocza: **`KREATOR_RZUTU_POMIESZCZENIA`**. Komenda pyta użytkownika o szerokość i głębokość pomieszczenia, automatycznie rysuje rzut z czterema ścianami (jako polilinia zamknięta) na warstwie ŚCIANY, dodaje okno i drzwi (parametrycznie) i wymiaruje. Pokazuje cały potencjał projektu w trzech minutach nagrania.

**Temat drugi — komenda przydatna na codziennej praktyce.**
Nazwa robocza: **`AUTONUMERACJA_ARKUSZY`**. Komenda iteruje po wszystkich arkuszach (layoutach) w bieżącym rysunku, dla każdego z nich znajduje pole tekstowe oznaczone tagiem `<NUMER_ARKUSZA>` i wstawia w to miejsce kolejny numer (na przykład A-001, A-002, A-003 ...). To jest realne narzędzie, którego biura projektowe potrzebują na codzień, a które dziś robią ręcznie. Mocny argument na szkoleniu wyjazdowym.

**Temat trzeci — komenda „wow" dla decydenta technicznego na webinarze.**
Nazwa robocza: **`GENERATOR_LEGENDY`**. Komenda iteruje po wszystkich blokach w bieżącym rysunku, zlicza wystąpienia każdego z nich, generuje tabelę legendy w wybranym przez użytkownika rogu rysunku — z nazwą bloku, ilością wystąpień i krótkim opisem (jeśli blok ma atrybut `OPIS`). To jest narzędzie, które oszczędza pół dnia pracy projektantowi pracującemu z dużymi rysunkami branżowymi.

## Kryteria akceptacji

- [ ] Robert wybrał jeden z trzech tematów (albo zaproponował własny, który zatwierdza Dawid)
- [ ] Komenda napisana przy pomocy pomocnika „GstarCAD Python Helper", po iteracji do działającej wersji
- [ ] Plik `przyklady-chlopcow/robert/<nazwa>.py` w gałęzi roboczej
- [ ] Komenda działa na rysunku testowym dostarczonym przez Dawida (albo na rysunku z dotychczasowej praktyki Roberta, jeśli ma odpowiedni)
- [ ] Plik `README.md` z opisem komendy w pięknym polskim, plus instrukcją użycia
- [ ] Dwa zrzuty ekranu albo (lepiej) krótkie nagranie pokazujące działanie komendy (na potrzeby przyszłego materiału marketingowego)
- [ ] Krótka notatka Roberta — jak ocenia użyteczność tej komendy dla swoich klientów szkoleniowych, czy zamierza ją pokazać na webinarze albo w podcaście

## Wskazówki

Każdy z trzech tematów ma inny profil. Pierwszy jest najlepszy do nagrania podcastowego (efekt wow w krótkim czasie). Drugi jest najlepszy do prezentacji u realnego klienta na szkoleniu wyjazdowym (rozwiązuje konkretny problem). Trzeci jest najlepszy do webinaru dla decydentów technicznych (mierzalna oszczędność czasu).

Robert wybiera ten, który najlepiej pasuje do jego najbliższych planów szkoleniowych. Jeśli ma własny pomysł, który widzi w realnych potrzebach klientów — Dawid najprawdopodobniej go zatwierdzi.

## Materiały odniesienia

- [`biblioteka-rag/przewodnik-systemowy.md`](../biblioteka-rag/przewodnik-systemowy.md)
- [`biblioteka-rag/przyklady/`](../biblioteka-rag/przyklady/) — pięć wzorcowych komend Dawida
- [`PLAN.md`](../PLAN.md) — sekcja o etapie trzecim (galeria mistrzowska), w którą Robert najprawdopodobniej wchodzi naturalnie
