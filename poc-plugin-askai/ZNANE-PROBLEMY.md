# Znane problemy i lekcje — pygcad + plugin ASKAI

Skrót tego, co empirycznie boli i czego się nauczyliśmy. Aktualizowane w miarę testów.
Ostatnia aktualizacja: **2026-07-12** (praca nocna: audyt wzorców + prompt caching + zestaw demo).

---

## 1. Luki w wiązaniu pygcad (🔴 — silnik C++ działa, psuje się warstwa Pythona)

Wszystkie potwierdzone przez to, że **te same operacje przechodzą przez bramę .NET** (`Gssoft.Gscad.*`)
— więc to defekt młodego wiązania pygcad (~rok), nie silnika. Rejestr zgłoszeń do GstarSoft:
`gstarcad-ai-wewnetrzne/zgloszenia-gstarsoft/`.

| Obszar | Objaw | Obejście |
|---|---|---|
| `GcDb3dPolyline` + `setClosed`/`setColorIndex` + append | **twardy crash GstarCAD do pulpitu** | nie używać; 2D `GcDbPolyline` + `addVertexAt` |
| `GcDb2dPolyline()` + `appendVertex` | crash na regenie (repro 4 maszyny) | lekka `GcDbPolyline` (2D) |
| `saveAs` na standalone-bazie | zapisuje **pusty plik** mimo `eOk` (append+transakcja bez różnicy) | operacje plikowe „bez otwierania" → brama .NET |
| **`GcDbHatch` kreskowanie** | `appendLoop` **nie istnieje** w wiązaniu (są tylko `appendLoopFromBoundary`/`appendMPolygonLoop` na innych klasach); enumy pod `GcDbHatch.*` nie `GcDb.*` | nie generować programowego wypełnienia — rysować obrys + `BHATCH`/`H` ręcznie, docelowo brama .NET (znalezione 2026-07-12 z audytu wzorców) |

**Zasada:** rdzeń produktu (user→AI→skrypt→„Wykonaj tutaj") stoi na zwalidowanym-stabilnym podzbiorze
(20 wzorców + prymitywy). Rzeczy crashogenne są na obrzeżach (headless plik, hatch, 3D-poly) i albo
je omijamy, albo idą przez bramę .NET. Poprawka GstarSoftu = bonus, nie zależność.

## 2. Namespace enumów NIE jest jednolity

Większość enumów żyje pod `GcDb.*` (`GcDb.OpenMode`, `GcDb.TextHorzMode`, `GcDb.TextVertMode`,
`GcDb.Planarity`), ale część jest zagnieżdżona w klasie encji (`GcDbHatch.HatchStyle`,
`GcDbHatch.HatchPatternType`, `GcDbHatch.HatchLoopType`). `GcDb.HatchStyle` → `AttributeError`.
Model potrafi zgadnąć źle. **Weryfikacja:** walidator `testy-stabilnosci/validate_pygcad.py`
(sprawdza konstruktory względem stubów) + reużywanie wzorców z przewodnika zamiast zgadywania.

## 3. `GcDbText()` — pusty konstruktor = crash (NAPRAWIONE w przewodniku)

`GcDbText` wymaga `(punkt, tekst[, styl[, wysokość[, obrót]]])`. Pusty `GcDbText()` → `TypeError`,
kładł np. siatkę osi. Przewodnik ma teraz kanoniczny wzorzec Text/label z konstruktorem z argumentami
(pitfall #3). Audyt 12 typów encji (2026-07-12) potwierdził: model generuje już poprawnie.

## 4. Streaming — `claude-sonnet-5` domyślnie robi extended thinking (NAPRAWIONE)

Złożone prompty gubiły kod: model przemyśliwał cały budżet tokenów (`stop=max_tokens`, kod=0), a cisza
na streamie w trakcie myślenia → **Cloudflare ubijał bezczynny tunel** (0 bajtów). Fix: `thinking={"type":"disabled"}`
+ `max_tokens=4096` w `backend/main.py`. Efekt: siatka osi 19 s(sam thinking) → 11 s(pełny kod).

## 5. Modeless „Wykonaj tutaj" — grafika live, tekst nie (znane ograniczenie)

Po `exec` plugin woła `gcedGraphScr()` (synchroniczny redraw) → **geometria pojawia się przy otwartym
oknie**. Ale komunikaty `gcedPrompt` czekają na zamknięcie okna (modal blokuje pompę wiersza poleceń).
Dla demo liczy się grafika → OK. `gcedRedraw(null,1)` rzuca `TypeError` w tym wiązaniu — użyty `gcedGraphScr()`.

## 6. Status wykonania nie może kłamać (plugin v0.5) — D8

`exec()` bez wyjątku **nie** dowodzi, że rysunek powstał: wygenerowany kod zwykle łapie własne błędy
w `try/except` i zgłasza je przez `gcedPrompt`. Plugin v0.5 mówi teraz „Kod wykonany (bez wyjątku Pythona)"
zamiast „pomyślnie".

**Pełne wykrywanie błędów wewnętrznych — projekt do zrobienia i weryfikacji na LC:**
Naiwne wstrzyknięcie shimu `gcedPrompt` do `exec_namespace` **nie zadziała** — wygenerowany kod zaczyna
się od `from pygcad.pygrx import *`, co nadpisuje wstrzyknięty symbol. Poprawne rozwiązanie: **monkey-patch
na poziomie modułu** przed exec, przywrócenie po (`try/finally`):
```python
import pygcad.pygrx as _px
_orig = _px.gcedPrompt
_captured = []
def _tee(s):
    _captured.append(str(s)); return _orig(s)
_px.gcedPrompt = _tee
try:
    exec(code, exec_namespace)         # import * podchwyci _tee z modułu
finally:
    _px.gcedPrompt = _orig
low = " ".join(_captured).lower()
if any(m in low for m in ("[błąd]", "[blad]", "traceback", "incompatible", "nie powiodło", "nieznane")):
    ...  # status: kod zgłosił błąd wewnętrzny
```
Wymaga testu na LC (interakcja `import *` z rebindem atrybutu modułu w realnym runtime pygcad) — nie
wdrażać w ciemno na ścieżce demo-krytycznej.

## 7. Fence markdown w trybie execute (obsłużone u odbiorcy)

Mimo dosłownej instrukcji „zero bloków markdown", model dokleja ```` ``` ```` w ~⅓ przypadków (dokręcanie
promptu nie pomaga — to zachowanie modelu, a bazowy przewodnik jest pełen fenced-code, co go primuje).
Niezawodny bezpiecznik = `AskaiDialog._extract_code()` w pluginie (regex wycina Python z fence'ów).

## 8. Prompt caching (backend)

System-prompt (~7,3k tok) idzie jako blok z `cache_control: ephemeral` → na powtórkach w oknie 5 min
input tego kawałka kosztuje 10% zamiast 100% (**~90% mniej**). `EXECUTE_INSTRUCTION` = osobny blok, więc
cache trafia w obu trybach. Backend loguje `usage: input/cache_create/cache_read/output` (docker logs) —
bieżący wgląd w koszt. Empirycznie: audyt 12 generacji = 12× `cache_read=7294`.

---

## Lekcje metodyczne

- **Waliduj lokalnie, nie generacjami.** Stuby `pygrx.pyi` (443 klasy, 37k linii) = grep/AST za 0 tokenów API.
  Konstruktory/metody sprawdza `validate_pygcad.py`. Koszt API tylko z realnej generacji przez backend.
- **Licz atrybuty, nie bloki.** Do testu atrybutów rysunek z 737 blokami może mieć 0 atrybutów. Zawsze
  mierz to, co test naprawdę ćwiczy (lekcja z doboru korpusu DWG 2026-07-12).
- **`saveAs=eOk` to nie dowód zapisu.** Trzeba odczytać zawartość z dysku (bug saveAs udawał sukces).
- **Bugi łapane dopiero end-to-end:** `eNotOpenForWrite`, brak `handle()` na `GcDbBlockReference`, kolizja
  cudzysłowów typograficznych w f-string przy APPLOAD — stuby dają sygnatury, ale runtime łapie tylko LC.
