# Protokół testu LC — 2026-07-12

Rzeczy z sesji nocnej, które wymagają oka na żywo w GstarCAD 2027 (render/runtime).
Wszystkie skrypty leżą na LC: `C:\Users\Public\gs-ai\test-lc-2026-07-12\`.
Każdy odpala się przez **`APPLOAD`** (rysuje od razu, bez wpisywania komendy).

> Setup (jeśli świeży start): Python 3.11.8 w PATH + `APPMANAGER` → „Interfejs Python" włączony.
> Widok: po każdym skrypcie `Z`↵`E`↵ (zakres), żeby zobaczyć całość. Pracuj na świeżym `NEW`.

## Testy — kolejność od najważniejszego

| # | Plik | Co ma się pojawić | Werdykt szukamy |
|---|---|---|---|
| **1** | `test_mpolygon.py` | prostokąt 400×200 **zakreskowany ANSI31** + komunikat `[MPOLY] appendLoop=.. setPattern=.. eval=..` | **Czy pygcad umie wypełnić kodem?** Jeśli tak → mamy hatch bez bramy .NET. Jeśli `[MPOLY BLAD] TypeError` na setPattern → to rozbieżność stub (`patName: int`) vs string — notujemy dokładny błąd |
| 2 | `2_siatka_osi.py` | siatka osi + kółka z literami **A–D / 1–3** | **czy tekst `GcDbText` się renderuje** (po naprawie pustego konstruktora) |
| 3 | `4_tabelka.py` | tabelka rysunkowa z 5 opisami tekstem | tekst + `GcDbPolyline` jako ramka |
| 4 | `5_wymiary.py` | prostokąt 1000×600 z **wymiarami** boków | `GcDbAlignedDimension` render |
| 5 | `1_bolt_circle.py` | rozstaw 8 śrub na okręgu podziałowym | okręgi + linie (najprostszy, sanity) |
| 6 | `3_schody.py` | rzut biegu schodów (10 stopni) | linie/serie |

## Jak zapisać wynik (krótko)

Dla każdego: **narysowało / nie narysowało / częściowo** + treść komunikatu z konsoli (zwł. dla #1).
Jak coś padnie — **dokładny tekst błędu** z konsoli GstarCAD (to on mówi, co poprawić).

## Co z tego wynika

- **#1 GcDbMPolygon** — jedyne realnie NOWE pytanie API. Rozstrzyga, czy kreskowanie w produkcie
  idzie natywnie w pygcad, czy musi przez bramę .NET (jak saveAs/2dPoly).
- **#2–6** — potwierdzenie, że zestaw demo faktycznie rysuje (kod już zwalidowany vs stuby;
  brakuje tylko obrazu). Po zielonym → demo webinarowe jest pewne.

## Poza tym protokołem (większa robota, nie drop-in)

- **D8 — pełne wykrywanie błędów w pluginie** (monkey-patch `pygcad.pygrx.gcedPrompt`): projekt gotowy
  w `../ZNANE-PROBLEMY.md`. Do wdrożenia w pluginie + test na LC osobno, nie w tej serii.
