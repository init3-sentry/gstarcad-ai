# fingerprint-instalator.ps1 - snapshot powierzchni, ktora dotyka instalator GSAI.
# READ-ONLY. Uruchom PRZED i PO instalacji -> diff dwoch snapshotow = co instalator
# realnie zmienil; po deinstalacji snapshot ma wrocic do bazy = dowod "czysto".
# Cel: kazda maszyna staje sie odtwarzalnym srodowiskiem testowym bez szukania dziewiczej.
#
# PURE ASCII (PowerShell 5.1 bez BOM czyta nie-ASCII jako ANSI i sypie parser).
# Uzycie:  powershell -NoProfile -ExecutionPolicy Bypass -File fingerprint-instalator.ps1
# Wyjscie: czytelny raport na stdout + linia FINGERPRINT=<sha> (skrot delty do szybkiego diff).

$ErrorActionPreference = "SilentlyContinue"
$lines = @()
function Emit($s){ $script:lines += $s; Write-Output $s }

Emit "=== FINGERPRINT INSTALATORA GSAI ==="
Emit ("host   : " + $env:COMPUTERNAME)
Emit ("kiedy  : " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Emit ("uzytkownik-sesji: " + $env:USERNAME)
Emit ""

# --- 1. PYTHON ---
Emit "--- PYTHON ---"
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) { Emit ("python na PATH: " + $py.Source); Emit ("wersja: " + (& python --version 2>&1)) }
else { Emit "python: BRAK na PATH" }
$pyReg = Get-ChildItem "HKLM:\SOFTWARE\Python\PythonCore" -ErrorAction SilentlyContinue
foreach ($k in $pyReg) { Emit ("HKLM PythonCore: " + $k.PSChildName) }
Emit ""

# --- 2. GSTARCAD (produkt) ---
Emit "--- GSTARCAD (produkt) ---"
$gsRoots = @("HKLM:\SOFTWARE\Gstarsoft\GstarCAD","HKLM:\SOFTWARE\WOW6432Node\Gstarsoft\GstarCAD")
$foundGs = $false
foreach ($root in $gsRoots) {
  Get-ChildItem $root -ErrorAction SilentlyContinue | ForEach-Object {
    $foundGs = $true
    $ver = $_.PSChildName
    $ip = (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).InstallPath
    Emit ("wersja: " + $ver + "   InstallPath: " + $ip)
  }
}
if (-not $foundGs) { Emit "GstarCAD: nie znaleziono w HKLM (moze zainstalowany per-user?)" }
Emit ""

# --- 3. STARTUP SUITE (to wpisuje instalator: HKU\<SID>\...\Appload\Startup) ---
Emit "--- STARTUP SUITE (Appload) per profil uzytkownika ---"
$anyProfile = $false
Get-ChildItem "Registry::HKEY_USERS" -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match "^S-1-5-21" -and $_.PSChildName -notmatch "_Classes$" } | ForEach-Object {
  $sid = $_.PSChildName
  $gsBase = "Registry::HKEY_USERS\$sid\Software\Gstarsoft\GstarCAD"
  Get-ChildItem $gsBase -ErrorAction SilentlyContinue | ForEach-Object {
    $rel = $_.PSChildName   # np. R27
    Get-ChildItem "$($_.PSPath)\Profiles" -ErrorAction SilentlyContinue | ForEach-Object {
      $prof = $_.PSChildName
      $startup = "$($_.PSPath)\Dialogs\Appload\Startup"
      $props = Get-ItemProperty $startup -ErrorAction SilentlyContinue
      if ($props) {
        $anyProfile = $true
        $num = $props.NumStartup
        Emit ("SID=$sid  $rel  profil='$prof'  NumStartup=$num")
        if ($props) {
          $props.PSObject.Properties | Where-Object { $_.Name -match "^Startup\d+$" } | Sort-Object Name | ForEach-Object {
            Emit ("    " + $_.Name + " = " + $_.Value)
          }
        }
      }
    }
  }
}
if (-not $anyProfile) { Emit "brak wpisow Startup Suite (albo profil GstarCAD nieuruchomiony ani razu)" }
Emit ""

# --- 4. PATH (maszyna + uzytkownik) - Python trafia tu ---
Emit "--- PATH ---"
$mp = [Environment]::GetEnvironmentVariable("Path","Machine")
$up = [Environment]::GetEnvironmentVariable("Path","User")
Emit ("Machine PATH pozycji: " + ($mp -split ';' | Where-Object {$_} ).Count)
($mp -split ';') | Where-Object { $_ -match "[Pp]ython" } | ForEach-Object { Emit ("  MACHINE python-path: " + $_) }
($up -split ';') | Where-Object { $_ -match "[Pp]ython" } | ForEach-Object { Emit ("  USER python-path: " + $_) }
Emit ""

# --- SKROT DELTY: hash powierzchni (bez czasu/hosta) do szybkiego 'czy sie zmienilo' ---
$surface = ($lines | Where-Object { $_ -notmatch "^kiedy|^host|^uzytkownik-sesji" }) -join "`n"
$sha = [System.BitConverter]::ToString(
  (New-Object Security.Cryptography.SHA256Managed).ComputeHash([Text.Encoding]::UTF8.GetBytes($surface))
).Replace("-","").ToLower()
Write-Output ("FINGERPRINT=" + $sha.Substring(0,16))
