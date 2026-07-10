# Python 3.11.8 — WYMAGANY runtime dla pygcad w GstarCAD 2027

Ten folder przechowuje **niezmienną kopię oficjalnego instalatora Python 3.11.8 (Windows x64)** — dokładnie tej wersji, której GstarCAD 2027 potrzebuje w systemie, żeby pygcad (Python w GstarCAD) w ogóle działał.

## ⚠️ Najważniejsze — to jest WYMAGANE, nie opcjonalne

**Wbrew wcześniejszemu założeniu, GstarCAD NIE działa z Pythonem „od razu po instalacji".** Empirycznie (2026-07-10, maszyna testowa): pygcad korzysta z **systemowego** Pythona 3.11.8 (64-bit) zainstalowanego i dodanego do **PATH** (`C:\Program Files\Python311\` w PATH, `python --version` → `Python 3.11.8`). Na świeżej maszynie **bez** tego, polecenie `APPLOAD` nie zarejestruje żadnej komendy z pliku `.py` — brakuje `python311.dll` na ścieżce.

Dlatego ta kopia ma trzy role:

1. **Wymóg wdrożeniowy (runtime).** To jest instalator, który trzeba postawić + dodać do PATH, żeby pygcad ruszył. Bez niego wtyczka ASKAI ani generowany kod nie zadziałają.
2. **Zabezpieczenie wersji (preservation).** Niezmienna, zahashowana kopia dokładnie tej wersji — gdyby python.org ją usunął/podmienił, zawsze mamy „to samo 3.11.8", z którym testowaliśmy.
3. **Środowisko deweloperskie.** `venv`/lint/backend zgodny z wersją, którą realnie wykonuje GstarCAD.

> **Otwarte pytanie (do Williama Wanga / GstarSoft R&D):** czy wymóg osobnej instalacji Pythona + PATH dotyczy **każdej** instalacji GstarCAD 2027, czy nasza instalacja testowa była niestandardowa? To ma wagę strategiczną — jeśli każdy klient musi instalować Pythona i grzebać w PATH, to uderza w obietnicę „load and run bez konfiguracji".

## Fakty o pliku

| Pole | Wartość |
|---|---|
| Plik | `python-3.11.8-amd64.exe` |
| Wersja | **3.11.8** (Windows, 64-bit) |
| Rozmiar | ~26 MB |
| Źródło | `https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe` |
| SHA256 | `fd3428eb6c80901b877d036ffa2be127ccad9bbe036a43f00fc96a48b724f9c7` |
| Pobrano | 2026-07-10 |
| Licencja | PSF License (redystrybucja dozwolona) |

> **Weryfikacja integralności (Windows PowerShell):**
> ```powershell
> Get-FileHash .\python-3.11.8-amd64.exe -Algorithm SHA256
> ```
> Hash musi zgadzać się z powyższym. (Warto też porównać z sumą publikowaną na stronie wydania python.org.)

## Potwierdzenie, że to ta sama wersja co w GstarCAD

Aby empirycznie sprawdzić, jakiego dokładnie Pythona ma dana instalacja GstarCAD-a, uruchom w GstarCAD komendę `DIAG_INFO` ze skryptu [`../../poc-plugin-askai/testy-stabilnosci/gstarcad-diag.py`](../../poc-plugin-askai/testy-stabilnosci/gstarcad-diag.py) — zaloguje `sys.version` wbudowanego interpretera do pliku na Pulpicie. Ta wartość to źródło prawdy; niniejszy plik ma jej odpowiadać.

## Instalacja (tylko dla deweloperów / środowiska dev)

1. Uruchom `python-3.11.8-amd64.exe`.
2. Zaznacz **„Add python.exe to PATH"** (ułatwia `venv`/`pip`).
3. Domyślna ścieżka instalacji: `C:\Users\<user>\AppData\Local\Programs\Python\Python311\` (per-user) albo `C:\Program Files\Python311\` (dla wszystkich).
4. Weryfikacja: `py -3.11 --version` → `Python 3.11.8`.
5. Środowisko zgodne z GstarCAD-em: `py -3.11 -m venv .venv-gstarcad`.

**Nie mieszać z interpreterem GstarCAD-a** — to osobne środowisko do pracy poza CAD-em.

## Uwaga o przechowywaniu w repo

Plik binarny (~26 MB) jest tu trzymany wprost w drzewie repo, żeby był pobieralny ze strony repozytorium z tym opisem. Jeśli w przyszłości rozmiar repo zacznie przeszkadzać, alternatywy: przenieść do **GitHub Release** (asset) albo **Git LFS** — bez zmiany tego opisu.
