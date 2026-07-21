<#
  gstarcad-ai — diagnostyka maszyny pod wtyczke Python w GstarCAD.
  Cel: JEDNYM wklejeniem pokazac, czy nowa maszyna ma wszystko, czego trzeba,
       i wychwycic przyczyne code:126 ZANIM zaczniemy (zwlaszcza niezgodnosc 64/32-bit).
  Uzycie: wklej CALY blok do PowerShell uruchomionego JAKO ADMINISTRATOR, Enter, wklej wynik.
#>
function Get-PEBitness($path){
  if(-not $path -or -not (Test-Path $path)){ return "BRAK PLIKU" }
  try{
    $fs=[IO.File]::OpenRead($path); $br=New-Object IO.BinaryReader($fs)
    $fs.Position=0x3C; $peOff=$br.ReadInt32(); $fs.Position=$peOff+4
    $m=$br.ReadUInt16(); $br.Close(); $fs.Close()
    switch($m){ 0x8664{"64-bit (x64)"} 0x14C{"32-bit (x86)"} 0xAA64{"ARM64"} default{("nieznana 0x{0:X}" -f $m)} }
  }catch{ "blad odczytu PE" }
}
$py=(& python -c "import sys;print(sys.base_prefix)" 2>$null); if($py){ $py=$py.Trim() }
$pyExe = if($py){ Join-Path $py 'python.exe' }     else { $null }
$pyDll = if($py){ Join-Path $py 'python311.dll' }  else { $null }
# Pod Gstarsoft bywa kilka gcad.exe (DWG FastView itd.) — wtyczka Python jest w GstarCAD 2027.
$allGcad = Get-ChildItem 'C:\Program Files\Gstarsoft','C:\Program Files (x86)\Gstarsoft' `
           -Recurse -Filter gcad.exe -ErrorAction SilentlyContinue
$g = $allGcad | Where-Object { $_.FullName -match 'GstarCAD' } | Select-Object -First 1
if (-not $g) { $g = $allGcad | Select-Object -First 1 }
$inPath = if($py){ [Environment]::GetEnvironmentVariable('Path','Machine') -like "*$py*" } else { $false }
""
"====== RAPORT MASZYNY (gstarcad-ai) ======"
"PYTHON home        : $py"
"python.exe bit     : $(if($pyExe){ Get-PEBitness $pyExe } else { 'BRAK PYTHONA' })"
"python311.dll jest : $(if($pyDll){ Test-Path $pyDll } else { '-' })"
"GstarCAD (gcad.exe): $($g.FullName)"
"wszystkie gcad.exe : $(($allGcad.FullName) -join '  |  ')"
"gcad.exe bit       : $(if($g){ Get-PEBitness $g.FullName } else { 'NIE ZNALEZIONO' })"
"dll obok gcad.exe  : $(if($g){ Test-Path (Join-Path $g.DirectoryName 'python311.dll') } else { '-' })"
"VCRUNTIME140       : $(Test-Path C:\Windows\System32\vcruntime140.dll) | 140_1: $(Test-Path C:\Windows\System32\vcruntime140_1.dll)"
"UCRT (ucrtbase)    : $(Test-Path C:\Windows\System32\ucrtbase.dll)"
"Python w PATH sys  : $inPath"
"=========================================="
"WAZNE: 'gcad.exe bit' oraz 'python.exe bit' MUSZA byc OBA 64-bit (x64)."
"       Rozne wartosci = to jest przyczyna code:126 (wtyczka pygrx jest x64-only)."
