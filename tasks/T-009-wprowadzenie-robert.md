# T-009 — Wprowadzenie do projektu: Robert Nowakowski

| Pole | Wartość |
|---|---|
| Identyfikator | T-009 |
| Etap | pierwszy |
| Przypisany do | **Robert Nowakowski** (robert.nowakowski [małpa] tmsys.pl) — stały współpracownik zewnętrzny TMSys, prowadzący firmę szkoleniową |
| Przewidywany czas | 6 godzin (rozłożone na cały tydzień, w wolnych przerwach między szkoleniami) |
| Status | oczekuje |
| Data wejścia | 2026-06-30 |
| Data deklarowanego ukończenia | 2026-07-14 |
| Zależy od | T-004 (zatwierdzenie pakietu wprowadzającego przez Dawida) |

## Cel

Wprowadzenie Roberta do projektu i jego unikalnej roli. Ponieważ Robert ma ponad dwadzieścia lat doświadczenia w branży CAD i prowadzi własną firmę szkoleniową, jego ścieżka wprowadzenia jest krótsza niż dla chłopaków z pomocy technicznej — zakładamy, że spora część materiału z pakietu wprowadzającego będzie dla niego oczywista, a pewne rzeczy może chcieć omówić od strony, którą my nie przewidzieliśmy (na przykład „jak prezentować tę funkcjonalność klientom szkoleniowym"). Robert jest też naszym pierwszym filtrem testowym dla samego pakietu — jego sceptyczne pytania pomogą nam ulepszyć materiały, zanim trafią do szerszego użytku.

## Kryteria akceptacji

- [ ] Przeczytane wszystkie pliki pakietu wprowadzającego (`dla-pomocy-technicznej/00` do `06`) — w tempie wygodnym dla Roberta, nie wymaga zatwierdzenia każdej lekcji osobno
- [ ] Skonfigurowane konto w ChatGPT Team TMSys, dostęp do pomocnika „GstarCAD Python Helper"
- [ ] Wykonane co najmniej pięć zapytań testowych do pomocnika, z których co najmniej jedno wymaga iteracji
- [ ] Pierwszy test załadowania wygenerowanego skryptu w GstarCAD 2026 przez `APPLOAD` — komenda zarejestrowana, działa
- [ ] Krótka notatka z obserwacjami zapisana do folderu `przeglady/2026-07-XX-feedback-robert.md` — to co Robert dostrzegł w naszych materiałach, gdzie widzi pułapki, jakie ma sugestie dla pakietu wprowadzającego

## Wskazówki

Robert nie jest w żaden sposób formalnym podwładnym Dawida — jest stałym współpracownikiem zewnętrznym z własną firmą. Dawid komunikuje się z nim partnersko, nie służbowo. Tempo pracy nad zadaniem dyktuje Robert sam, w ramach swoich pozostałych zobowiązań szkoleniowych.

Robert jest naszym najcenniejszym testerem na tym etapie. Każda jego uwaga dotycząca pakietu wprowadzającego jest cenna i powinna zostać przekazana do Claude'a (przez Dawida) jako wskazówka do iteracji materiałów. Robert widzi rzeczy, których chłopcy z pomocy mogą nie zauważyć, bo perspektywa szkoleniowca jest inna niż perspektywa wsparcia technicznego.

## Materiały odniesienia

- Wszystkie pliki w folderze [`dla-pomocy-technicznej/`](../dla-pomocy-technicznej/)
- [`poc-plugin-askai/backend/system-prompt.md`](../poc-plugin-askai/backend/system-prompt.md)
- [`biblioteka-rag/przyklady/`](../biblioteka-rag/przyklady/) — pięć wzorcowych komend
- [`PLAN.md`](../PLAN.md) — mapa drogowa, żeby Robert zobaczył perspektywę półroczną i znalazł swoje miejsce
