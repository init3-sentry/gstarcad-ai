<#
  Komponent instalatora gstarcad-ai — udostępnia python311.dll GstarCADowi.
  Rozwiązuje błąd "Moduł interfejsu Python załadowany nieprawidłowo (code:126)".

  Robi OBA niezawodne sposoby naraz (celowo — nie zależymy od jednego):
    (A) kopiuje python311.dll obok gcad.exe  -> działa OD RAZU, bez restartu Windows
                                                (folder aplikacji = 1. w kolejności ładowania DLL)
    (B) dodaje folder Pythona do PATH systemowego -> czysta metoda na przyszłość
                                                     (pełny Python home; działa po restarcie sesji)

  Uruchom jako ADMINISTRATOR (pisze do Program Files i PATH systemowego).
  Docelowo tę logikę wywoła instalator (Inno/NSIS) w tle. Tu = wersja skryptowa do walidacji.
#>
$ErrorActionPreference = 'Stop'
Write-Host "== gstarcad-ai: konfiguracja Python dla GstarCAD =="

function Get-PEBitness($path){
    if(-not $path -or -not (Test-Path $path)){ return $null }
    try{
        $fs=[IO.File]::OpenRead($path); $br=New-Object IO.BinaryReader($fs)
        $fs.Position=0x3C; $peOff=$br.ReadInt32(); $fs.Position=$peOff+4
        $m=$br.ReadUInt16(); $br.Close(); $fs.Close(); return $m
    }catch{ return $null }
}

# --- 1. Wykryj Pythona 3.11.8 (przez sys.base_prefix — działa nawet gdy folder nie jest w PATH) ---
try   { $pyHome = (& python -c "import sys; print(sys.base_prefix)" 2>$null).Trim() }
catch { $pyHome = $null }

if (-not $pyHome -or -not (Test-Path (Join-Path $pyHome 'python311.dll'))) {
    Write-Host "[BLAD] Nie wykryto Pythona 3.11.8 z python311.dll."
    Write-Host "       Zainstaluj Python 3.11.8 (amd64) i uruchom skrypt ponownie."
    exit 1
}
$pyDll = Join-Path $pyHome 'python311.dll'
Write-Host "  Python 3.11.8: $pyHome"

# --- 2. Znajdź gcad.exe (folder instalacji GstarCAD) ---
$gcad = Get-ChildItem 'C:\Program Files\Gstarsoft','C:\Program Files (x86)\Gstarsoft' `
        -Recurse -Filter gcad.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $gcad) {
    Write-Host "[BLAD] Nie znaleziono gcad.exe w C:\Program Files\Gstarsoft."
    Write-Host "       Podaj ścieżkę instalacji GstarCAD — poprawię skrypt."
    exit 1
}
$gcadDir = $gcad.DirectoryName
Write-Host "  GstarCAD:      $gcadDir"

# --- 2b. STRAZNIK ARCHITEKTURY: gcad.exe i python311.dll musza byc oba 64-bit ---
#     Wtyczka pygrx jest x64-only (pygrx.gcp: Platform="x64"). Niezgodnosc = pewne code:126.
$gcadBit = Get-PEBitness $gcad.FullName
$pyBit   = Get-PEBitness $pyDll
if ($gcadBit -ne 0x8664) {
    Write-Host "[BLAD] gcad.exe nie jest 64-bit (0x$('{0:X}' -f $gcadBit)). Wtyczka Python wymaga GstarCAD x64."
    exit 1
}
if ($pyBit -ne 0x8664) {
    Write-Host "[BLAD] python311.dll nie jest 64-bit (0x$('{0:X}' -f $pyBit))."
    Write-Host "       Zainstaluj Python 3.11.x w wersji 64-bit (Windows installer amd64) i powtorz."
    exit 1
}
Write-Host "  Architektura:  gcad.exe = x64, python311.dll = x64 (zgodne)"

# --- 3A. Metoda natychmiastowa: python311.dll obok gcad.exe ---
Copy-Item $pyDll -Destination $gcadDir -Force
Write-Host "  [OK] python311.dll skopiowana obok gcad.exe (działa od razu, bez restartu)"

# --- 3B. Metoda czysta na przyszłość: folder Pythona w PATH systemowym ---
$machinePath = [Environment]::GetEnvironmentVariable('Path','Machine')
if ($machinePath -notlike "*$pyHome*") {
    [Environment]::SetEnvironmentVariable('Path', ($machinePath.TrimEnd(';') + ';' + $pyHome), 'Machine')
    Write-Host "  [OK] $pyHome dodane do PATH systemowego (pełny Python home po restarcie sesji)"
} else {
    Write-Host "  [OK] Python już jest w PATH systemowym"
}

Write-Host ""
Write-Host "GOTOWE."
Write-Host "  1. Zamknij GstarCAD CAŁKOWICIE."
Write-Host "  2. Odpal na nowo, włącz wtyczkę Python (AppManager)."
Write-Host "  3. Jeśli wstaje BEZ code:126 — komponent zwalidowany, wchodzi do instalatora."
