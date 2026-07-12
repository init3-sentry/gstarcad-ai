#!/usr/bin/env bash
# Synchronizuje wzorce z repo na LightCatcher do JEDNEGO udokumentowanego miejsca.
#
# Źródło (repo):  biblioteka-rag/przyklady/*.py  +  przyklady/dane-testowe/*
# Cel (LC):       C:\Users\Public\gs-ai\wzorce\  +  ...\wzorce\dane-testowe\
#
# LC = lustro repo. NIE wrzucamy skryptów ad-hoc na Desktop (patrz reguła lokalizacji
# w biblioteka-rag/przyklady/README.md). Uruchom po każdym dodaniu/zmianie wzorca:
#   ./skrypty/sync-wzorce-to-lc.sh
#
# Wymaga aliasu SSH `lightcatcher` (~/.ssh/config). Shell LC = PowerShell.
set -euo pipefail

LC="lightcatcher"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_DIR/biblioteka-rag/przyklady"
DST="C:/Users/Public/gs-ai/wzorce"

echo "[sync-lc] źródło: $SRC"
echo "[sync-lc] cel:    $LC:$DST"

# 1) struktura docelowa (idempotentnie)
ssh -o ConnectTimeout=8 "$LC" \
  'powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path C:\Users\Public\gs-ai\wzorce\dane-testowe | Out-Null"'

# 2) wzorce (.py z korzenia przyklady/)
scp -q -o ConnectTimeout=10 "$SRC"/*.py "$LC:$DST/"

# 3) dane testowe
scp -q -o ConnectTimeout=10 "$SRC"/dane-testowe/* "$LC:$DST/dane-testowe/"

# 4) raport
echo "[sync-lc] wgrane wzorce:"
ssh -o ConnectTimeout=8 "$LC" \
  'powershell -NoProfile -Command "(Get-ChildItem C:\Users\Public\gs-ai\wzorce -Filter *.py).Count; Write-Output plikow-py; (Get-ChildItem C:\Users\Public\gs-ai\wzorce\dane-testowe).Count; Write-Output plikow-danych"'
echo "[sync-lc] gotowe. Na LC: APPLOAD z C:\\Users\\Public\\gs-ai\\wzorce\\"
