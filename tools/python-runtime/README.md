# Python 3.11.8 — zabezpieczona wersja runtime dla GstarCAD 2027

Ten folder przechowuje **niezmienną kopię oficjalnego instalatora Python 3.11.8 (Windows x64)** — tej samej wersji, którą GstarCAD 2027 ma **wbudowaną** we własnej instalacji jako środowisko uruchomieniowe dla pygcad.

## ⚠️ Najważniejsze — przeczytaj zanim komuś każesz to instalować

**GstarCAD ma tego Pythona wbudowanego.** Klient GstarCAD-a **niczego nie instaluje** — interpreter 3.11.8 jest częścią instalacji GstarCAD-a (wewnątrz `plugins/pygrx.bundle/…`), a polecenie `APPLOAD` używa właśnie jego. **Zainstalowanie tego pliku NIE zmienia interpretera, którego używa pygcad** i **NIE jest potrzebne do działania wtyczek ani generowanego kodu.**

Po co więc trzymamy tę kopię — dwa realne powody:

1. **Zabezpieczenie wersji (preservation).** Chcemy mieć niezmienną, zahashowaną kopię dokładnie tej wersji, gdyby python.org kiedyś ją usunął albo podmienił. Dzięki temu zawsze wiemy i mamy „to samo 3.11.8", z którym testowaliśmy.
2. **Środowisko deweloperskie.** Gdy ktoś z zespołu chce lokalnie sprawdzić składnię generowanych skryptów, uruchomić backend albo zrobić `venv` **zgodny z wersją GstarCAD-a**, instaluje dokładnie tę wersję — żeby dev-środowisko odpowiadało temu, co realnie wykonuje GstarCAD.

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
