<#
  encode-tool.ps1 - JEDNA KOMENDA: zwalidowany  *_logic.py  ->  chroniony .pyd + folder dist.
  Zamyka reczna dlubanine z README-cython.md (setup.py + build_ext + rename + strip) w jeden krok.

  UWAGA: plik CELOWO w czystym ASCII (bez polskich znakow i myslnikow). PowerShell 5.1 czyta
  .ps1 bez BOM jako Windows-1252 i mangluje UTF-8 (np. em-dash -> a trailing " -> parse error).

  Budowa .pyd wymaga Windows + Python 3.11 x64 (jak GstarCAD). Uruchamiac na maszynie testowej.

  Jednorazowo - toolchain (MSVC BuildTools + Cython):
      .\encode-tool.ps1 -Setup

  Zakodowanie narzedzia (logika -> .pyd; do dist trafia .pyd + loader, BEZ zrodel):
      .\encode-tool.ps1 -Logic .\demo_logic.py -Loader .\demo_loader.py -Dist .\dist

  Wynik: <dist>\<nazwa>.pyd + <loader>.py. APPLOAD loadera w GstarCAD -> komenda dziala,
  a zrodlo logiki (.py/.c) NIE opuszcza maszyny buildu. Wzorzec API: patrz README-cython.md.
#>
param(
    [string]$Logic,
    [string]$Loader,
    [string]$Dist = ".\dist",
    [switch]$Setup
)
$ErrorActionPreference = 'Stop'

if ($Setup) {
    Write-Host "== Toolchain (jednorazowo) =="
    if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
        Write-Host "  Instaluje MSVC C++ BuildTools (kilka GB, kilka min)..."
        curl.exe -sL -o "$env:TEMP\vs_BuildTools.exe" https://aka.ms/vs/17/release/vs_BuildTools.exe
        & "$env:TEMP\vs_BuildTools.exe" --quiet --wait --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended
    } else { Write-Host "  cl.exe juz jest - pomijam BuildTools" }
    python -m pip install --quiet --upgrade cython
    Write-Host "[OK] Toolchain gotowy (MSVC + Cython)."
    if (-not $Logic) { return }
}

if (-not $Logic)             { throw "Podaj -Logic (sciezka do *_logic.py), albo -Setup do instalacji." }
if (-not (Test-Path $Logic)) { throw "Nie ma pliku: $Logic" }

$logicFull = (Resolve-Path $Logic).Path
$logicDir  = Split-Path -Parent $logicFull
$logicBase = [IO.Path]::GetFileName($logicFull)                 # np. audytz_logic.py
$logicName = [IO.Path]::GetFileNameWithoutExtension($logicFull) # np. audytz_logic

Write-Host "== Kompilacja $logicBase -> .pyd (Cython) =="
Push-Location $logicDir
try {
    # Generujemy tymczasowy setup.py = zwalidowana forma z README-cython.md
    # (python setup.py build_ext --inplace). setuptools sam znajduje MSVC przez vswhere.
    $tmpSetup = Join-Path $logicDir "_encode_setup.py"
    $setupBody = "from setuptools import setup`r`nfrom Cython.Build import cythonize`r`nsetup(ext_modules=cythonize(r'$logicBase', language_level=3))`r`n"
    Set-Content -Path $tmpSetup -Value $setupBody -Encoding ascii
    python $tmpSetup build_ext --inplace
    $rc = $LASTEXITCODE
    Remove-Item $tmpSetup -ErrorAction SilentlyContinue
    if ($rc -ne 0) { throw "Build Cython zwrocil blad ($rc)." }
    $pyd = Get-ChildItem -Filter "$logicName*.pyd" | Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $pyd) { throw "Build nie wyprodukowal .pyd (sprawdz komunikaty wyzej)." }
}
finally { Pop-Location }

Write-Host "== Dist: tylko .pyd + loader, zero zrodel =="
New-Item -ItemType Directory -Force -Path $Dist | Out-Null
$distPyd = Join-Path $Dist "$logicName.pyd"                     # czysta nazwa bez tagu ABI (import ok)
Copy-Item $pyd.FullName $distPyd -Force
if ($Loader) {
    if (-not (Test-Path $Loader)) { throw "Nie ma loadera: $Loader" }
    Copy-Item (Resolve-Path $Loader).Path $Dist -Force
}

# sprzatanie artefaktow buildu w zrodle (zeby nie zostawal .c ani build\)
Remove-Item (Join-Path $logicDir "$logicName.c") -ErrorAction SilentlyContinue
Remove-Item (Join-Path $logicDir "build") -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "[OK] $logicName.pyd -> $Dist"
Write-Host "Dist zawiera:"
Get-ChildItem $Dist | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""
Write-Host "Dalej: APPLOAD loadera z dist w GstarCAD -> komenda dziala, a logika (.py/.c) tam NIE trafia."
