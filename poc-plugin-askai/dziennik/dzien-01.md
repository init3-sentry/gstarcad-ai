# Dziennik testów — dzień 1

**Data:** 1 lipca 2026
**Wykonawca:** Dawid Jakubowski
**Środowisko:** Windows LightCatcher (home)
**Wersje GstarCAD do testowania:** 2026 oraz 2027 (równocześnie)

## Zakres dnia

Ładowanie pliku `plugin-askai-poc.py` przez `APPLOAD` w GstarCAD, uruchomienie komendy `ASKAI`, weryfikacja że okno tkinter otwiera się i nie zawiesza GstarCAD-a. Zgodnie z planem PoC (`../README.md` sekcja "Dzień pierwszy").

## Pre-flight — do zrobienia PRZED uruchomieniem APPLOAD

Zanim usiądziesz do właściwych testów, przejdź listę weryfikacyjną. Ratuje 20 minut miotania się jak coś nie zadziała.

### Środowisko sieciowe

- [ ] **LightCatcher (Windows) uruchomiony** — jeśli w S5, wysłać WoL z MBP przez skrypt (`lc-on` z `~/Code/init3-cortex/operations/lightcatcher-power-mgmt.md`)
- [ ] **Internet na LightCatcher działa** — sprawdź w przeglądarce `https://google.com`
- [ ] **Backend PoC odpowiada** — w przeglądarce na LC otwórz `https://gs-ai.init3.pro/health`. Powinieneś zobaczyć JSON z `"status": "ok"` i `"stage": "stub"` (jeśli `real-anthropic` — świetnie, klucz już wprowadzony)
- [ ] **Firewall Windows nie blokuje HTTPS** — jeśli `curl` z PowerShell na `https://gs-ai.init3.pro/health` nie odpowiada, sprawdź czy Windows Defender nie blokuje Pythonowego HTTP klienta

### GstarCAD 2026

- [ ] **GstarCAD 2026 zainstalowany i uruchamia się** — sprawdź wersję w `About` (menu Pomoc)
- [ ] **Python 3.11.8 wykrywany** — wpisz w wierszu poleceń `PYTHON`, powinien otworzyć się interpreter lub potwierdzenie że jest zainstalowany
- [ ] **APPLOAD komenda działa** — wpisz `APPLOAD`, powinno się otworzyć okno wyboru pliku

### GstarCAD 2027

- [ ] **GstarCAD 2027 zainstalowany i uruchamia się** — sprawdź wersję w `About`. **Uwaga:** 2027 wyszedł dopiero 1 lipca 2026 (dziś), pełna dokumentacja pygcad może być niekompletna. Empiryczna weryfikacja to jest punkt tego testu.
- [ ] **Python 3.11.8 wykrywany** (albo nowsza — sprawdź co GstarCAD 2027 dostarcza)
- [ ] **APPLOAD komenda działa** — analogicznie
- [ ] **Obie wersje uruchamiają się równolegle** — bez konfliktu, każda w swoim procesie

### Plik pluginu

- [ ] **Plik `plugin-askai-poc.py` pobrany** — z GitHub `https://raw.githubusercontent.com/init3-sentry/gstarcad-ai/main/poc-plugin-askai/plugin-askai-poc.py`, zapisany lokalnie na LightCatcher (np. na Pulpicie)
- [ ] **Zawartość zaczyna się od komentarza `# Plugin ASKAI dla GstarCAD 2026 — Proof of Concept`** — jeśli zaczyna się od `<!DOCTYPE html>`, przeglądarka zapisała HTML zamiast raw pliku. Kliknij prawym na link → „Zapisz jako", lub użyj `curl -o plugin-askai-poc.py <URL>`.

### Bezpieczna wersja rysunku

- [ ] **Nowy pusty rysunek** — NIE testuj na rzeczywistym projekcie klienta. Utwórz świeży `Nowy rysunek` przed każdym testem `Wykonaj tutaj`. Kod z backendu w trybie stub rysuje okrąg w punkcie (0, 0) — na pustym rysunku nic nie zniszczy, na projekcie klienta może nadpisać coś istniejącego.

---

## Kryterium zaliczenia

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
