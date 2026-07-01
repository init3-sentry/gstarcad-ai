# Dziennik testów — dzień 1

**Data:** 1 lipca 2026
**Wykonawca:** Dawid Jakubowski
**Środowisko:** Windows LightCatcher (home)
**Wersje GstarCAD do testowania:** 2026 oraz 2027 (równocześnie)

## Zakres dnia

Ładowanie pliku `plugin-askai-poc.py` przez `APPLOAD` w GstarCAD, uruchomienie komendy `ASKAI`, weryfikacja że okno tkinter otwiera się i nie zawiesza GstarCAD-a. Zgodnie z planem PoC (`../README.md` sekcja "Dzień pierwszy").

## Kryterium zaliczenia

Komenda `ASKAI` rejestruje się po `APPLOAD`, dialog otwiera i zamyka się bez zawieszania GstarCAD-a. Test wykonany równolegle w wersji 2026 i 2027 na osobnej maszynie Dawida.

Uwaga: dzień 1 planu przewiduje "banalny dialog". Nasz plugin realizuje od razu **dni 1-4** w jednym pliku (backend na sentry-cloud gotowy od 1 lipca południa) — jeśli wszystko pójdzie gładko, dzień 1 zaliczy przy pierwszym uruchomieniu, a resztę dni sprawdzimy w tej samej sesji testowej.

## Obserwacje z uruchomienia

### GstarCAD 2026

- [ ] Plik załadowany przez APPLOAD bez błędu?
- [ ] Komenda ASKAI zarejestrowana i widoczna w wierszu poleceń?
- [ ] Okno tkinter otwiera się?
- [ ] Pole tekstowe i przyciski działają wizualnie poprawnie?
- [ ] Wciśnięcie "Zamknij" zamyka okno bez zawieszania GstarCAD-a?

Notatki:

```
(wpisz obserwacje tutaj po teście)
```

### GstarCAD 2027

- [ ] Plik załadowany przez APPLOAD bez błędu?
- [ ] Komenda ASKAI zarejestrowana i widoczna w wierszu poleceń?
- [ ] Okno tkinter otwiera się?
- [ ] Pole tekstowe i przyciski działają wizualnie poprawnie?
- [ ] Wciśnięcie "Zamknij" zamyka okno bez zawieszania GstarCAD-a?

Notatki:

```
(wpisz obserwacje tutaj po teście)
```

## Różnice między wersjami

```
(jeśli zauważono jakiekolwiek różnice w zachowaniu, opisz tutaj — kluczowe
dla wyboru scenariusza A/B/C na koniec tygodnia)
```

## Napotkane problemy

```
(techniczne błędy, komunikaty, dziwne zachowania — wszystko warto zanotować)
```

## Wnioski i plan na jutro

```
(co dalej — kontynuujemy do dnia 2 / 3 / 4? Czy musimy się cofnąć?)
```
