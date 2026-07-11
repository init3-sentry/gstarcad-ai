# Zestaw demo ASKAI — kandydaci na webinar (GstarCAD 2027)

Pięć poleceń w języku naturalnym, które backend ASKAI zamienia na działający pygcad.
Dobrane pod **pokaz na żywo**: opierają się **wyłącznie na zweryfikowanych typach encji**
(linia, okrąg, łuk, tekst, polilinia 2D, wymiar liniowy), rysują w **dużej, widocznej skali**
(setki–tysiące jednostek, żeby wpadały w domyślny widok bez zoomowania) i pokazują rzeczy,
które CAD-owiec od razu rozpoznaje.

Pliki `.py` obok to **kod zwrócony przez model** (tryb `mode=execute`), zachowany jako gotowiec
awaryjny — na webinarze AI generuje na żywo, ale gdyby sieć/model zawiodły, ten sam efekt
odpalisz z `APPLOAD`.

## Status weryfikacji

- ✅ **Kod zwalidowany lokalnie** względem stubów pygcad (`pygrx.pyi`, 443 klasy) —
  0 błędnych konstruktorów/metod — oraz `py_compile` (składnia OK). Skrypt walidatora:
  `poc-plugin-askai/testy-stabilnosci/` (patrz raport nocny).
- 🟡 **Wizualny render na LC — do potwierdzenia przed webinarem.** Konstruktory i namespace'y
  są poprawne, ale finalny obraz na GstarCAD 2027 trzeba raz przejechać ręcznie (tekst
  `GcDbText` renderuje się po naprawie pustego konstruktora — patrz przewodnik pitfall #3).
  **Nie pokazuj na żywo tego, czego wcześniej nie odpaliłeś na LC.**

## Polecenia (skopiuj do pola ASKAI)

| # | Plik | Polecenie | Co rysuje | Typy encji |
|---|---|---|---|---|
| 1 | `1_bolt_circle.py` | „Narysuj rozstaw 8 śrub: osiem okręgów r=20 równomiernie na okręgu podziałowym r=400 wokół (0,0), plus okrąg podziałowy i krzyż środka." | rozstaw śrub (mechanika) | okrąg, linia |
| 2 | `2_siatka_osi.py` | „Narysuj siatkę osi konstrukcyjnych: 4 osie pionowe co 500 i 3 poziome co 500, każda zakończona kółkiem z literą/cyfrą (A-D, 1-3)." | siatka osi (architektura) | linia, okrąg, tekst |
| 3 | `3_schody.py` | „Narysuj rzut biegu schodów: 10 linii stopni co 300, szerokość 1200, plus linia biegu." | schody w rzucie | linia |
| 4 | `4_tabelka.py` | „Narysuj tabelkę rysunkową 1800×600: ramka + podział + pola Projekt/Rysował/Data/Skala/Nr rysunku." | tabelka rysunkowa | polilinia, linia, tekst |
| 5 | `5_wymiary.py` | „Narysuj prostokąt 1000×600 i dodaj wymiar liniowy boku poziomego i pionowego." | prostokąt z wymiarami | polilinia, wymiar |

## Dlaczego akurat te

- **Rozpoznawalność:** rozstaw śrub, siatka osi, tabelka i wymiary to rzeczy, które każdy
  odbiorca webinaru robi ręcznie codziennie — „AI zrobiło to jednym zdaniem" trafia od razu.
- **Bezpieczeństwo pokazu:** żaden nie dotyka kreskowania (`hatch` — 🔴 niezweryfikowane
  w wiązaniu pygcad, patrz przewodnik) ani `GcDb2dPolyline`/`saveAs` (znane bugi wiązania).
- **Skala:** wszystkie lądują w widocznym kadrze bez pan/zoom — istotne, bo pokaz idzie
  na żywo (patrz [feedback: rozmiar widoku demo]).

## Wersje: webinar vs rolka

- **Webinar (~500 osób):** 2-3 polecenia na żywo (siatka osi + tabelka są najmocniejsze
  narracyjnie), z kadrem ustawionym raz przed pokazem (`Z`↵`E`↵ = zakres).
- **Rolka TikTok/Instagram (później):** jedno polecenie, jeden cięty ujęciem efekt
  „zdanie → rysunek", najlepiej rozstaw śrub albo siatka osi (czytelne w pionie).
