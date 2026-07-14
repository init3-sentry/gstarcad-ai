# Szyfrowanie narzędzi — Cython .pyd (receptura na LC)

Cel: skompilować logikę do natywnego `.pyd` (niedekompilowalny), ładowanego przez cienki otwarty
`.py` wrapper. Mocniejsze niż `.pyc` (który już zwalidowany — dekompilowalny, lekka ochrona).

## ✅ ZWALIDOWANE END-TO-END (LC, GstarCAD 2027 SP1, 2026-07-14)

Bramka #2 PRZESZŁA: skompilowany `secret_demo.pyd` (folder BEZ źródła, tylko loader + .pyd) po `APPLOAD loader_secret.py` + `TESTPYD` wypisał `=== secret_demo.pyd DZIALA ... ===`. Ochrona IP działa — narzędzia można wydawać jako compiled `.pyd` + otwarty loader.

**Działająca receptura (dokładnie te kroki, ~5 min na 8GbE):**
```powershell
# 1) kompilator — bootstrapper VS BuildTools (pewniejszy headless niż winget):
curl -sL -o vs_BuildTools.exe https://aka.ms/vs/17/release/vs_BuildTools.exe
vs_BuildTools.exe --quiet --wait --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended
# 2) cython:
python -m pip install cython
# 3) build (setuptools SAM znajduje MSVC przez vswhere — vcvars NIE trzeba):
python setup.py build_ext --inplace     # -> secret_demo.cp311-win_amd64.pyd w folderze
# 4) do folderu dystrybucji TYLKO .pyd (jako secret_demo.pyd) + otwarty loader, bez .py/.c:
copy secret_demo.cp311-win_amd64.pyd  <dist>\secret_demo.pyd
# 5) GstarCAD (otwarty rysunek): APPLOAD <dist>\loader_secret.py -> TESTPYD
```
Kluczowe lekcje: (a) `.pyd` **nie importuje pygcad** — loader przekazuje API (patrz sekcja niżej); (b) `build_ext --inplace` kładzie `.pyd` w KORZENIU folderu (nie w `build\lib...`); (c) setuptools lokalizuje cl.exe sam po instalacji BuildTools.

## Warunki
- GstarCAD jedzie na CPython **3.11.8 x64** → `.pyd` musi być **cp311-win_amd64**.
- LC ma: Python 3.11.8 + `Python.h` + `python3.lib` (zweryfikowane). Brakuje: kompilatora C + Cython.

## Kroki na LC (gdy włączony)
```powershell
# 1) MSVC Build Tools (C++), jednorazowo — kilka GB:
winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
# 2) Cython:
python -m pip install cython
# 3) Build .pyd (w folderze szyfrowanie/):
python -m cython -3 --embed=false secret_demo.py   # -> secret_demo.c
# lub prosciej, jednym strzalem (kompiluje + linkuje w miejscu):
python -c "from Cython.Build import cythonize; cythonize('secret_demo.py', language_level=3)"
python setup.py build_ext --inplace   # jesli setup.py; albo uzyj 'cythonize -i secret_demo.py'
# 4) Zostaw TYLKO .pyd (usun .py i .c), przenies do folderu testowego:
#    New-Item C:\Users\Public\gs-ai\szyfr-test -ItemType Directory -Force
#    Copy secret_demo.*.pyd -> szyfr-test\secret_demo.pyd ; usun zrodla
```

## Test w GstarCAD (bramka #2)
1. Otworz GstarCAD, Interfejs Python = Uruchomione.
2. APPLOAD `loader_secret.py`.
3. Wpisz `TESTPYD`.
4. Sukces = `secret_demo.pyd DZIALA ...` → **skompilowany .pyd wykonuje logike i siega API GstarCAD** → cala ochrona OK.
   Porazka (import error / crash) → ABI/sciezka; diagnozujemy.

## WAZNE — wzorzec przekazywania API (nauczka Rafal 2026-07-14)
Skompilowany/importowany modul **nie widzi API pygcad** ani przez jawny import
(`ImportError: cannot import name`), ani przez `import *` (`NameError` przy wywolaniu —
nazwy sa wstrzykiwane tylko do pliku APPLOAD-owanego). Dlatego:
- **`.pyd` NIE importuje pygcad.** Jego funkcje przyjmuja potrzebne API jako argumenty.
- **Loader** (`.py`, APPLOAD-owany, ma API przez `import *`) **przekazuje** je do `.pyd`.
  Wzorzec: `secret_demo.run(gcdbWorkingDatabase, gcutPrintf)`.
Ten sam wzorzec stosujemy potem do realnych narzedzi (logika w `.pyd`, API z loadera).

### Realne narzedzie (wiele nazw API) — ZWALIDOWANE na AUDYTZ (LC 2026-07-14)
Dla narzedzia z kilkunastoma nazwami API nie przekazujemy ich pojedynczo. Loader podaje
CALE swoje `globals()`, a modul wstrzykuje je do siebie:
- **Loader** (`*_loader.py`, otwarty, APPLOAD): `@command` -> `logika.run(globals())`.
- **Logika** (`*_logic.py`, kompilowana): `def run(api): globals().update(api); _praca()`.
- **KRYTYCZNE dla Cythona:** wszystkie uzyte nazwy API MUSZA byc **zadeklarowane** na
  poziomie modulu (`gcdbWorkingDatabase = GcDb = ... = None`), inaczej blad kompilacji
  `undeclared name not builtin`. `globals().update(api)` podmienia None na realne funkcje
  przed uzyciem. Miss w liscie deklaracji = Cython wskaze ktora nazwe dodac.
Pilot: `szyfrowanie/pilot-audytz/` (audytz_logic.py + audytz_loader.py + setup_audytz.py).

## Po sukcesie
- Docelowo: logika narzedzi (21/22/23/... + konwersje Lee Mac) jako `.pyd`, cienkie `.py` wrappery @command,
  spiete instalatorem (patrz gstarcad-ai-wewnetrzne/dodatek-gstarcad/00-plan-research.md).
