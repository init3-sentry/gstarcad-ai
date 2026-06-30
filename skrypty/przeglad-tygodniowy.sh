#!/bin/bash
# ============================================================================
# Cotygodniowa procedura nadzorcza projektu gstarcad-ai
# ============================================================================
#
# Co robi:
#   1. Pobiera świeży stan publicznego repozytorium gstarcad-ai
#   2. Czyta wszystkie pliki zadań w folderze tasks/ i klasyfikuje je po statusie
#   3. Czyta git log z ostatnich siedmiu dni i nakłada zatwierdzenia na zadania
#   4. Generuje raport tygodniowy w folderze przeglady/
#   5. Zatwierdza i wypycha raport
#   6. Wysyła powiadomienie push przez ntfy.init3.pro do Dawida
#
# Uruchamiane przez:
#   procedurę launchd (~/Library/LaunchAgents/pro.init3.tygodniowy-przeglad-gstarcad.plist)
#   co piątek o godzinie 8:00 czasu lokalnego
#
# Wymaga:
#   - gh (GitHub CLI) zalogowane jako init3-sentry
#   - źródłowy plik środowiska: ~/.config/init3/load-env.sh (NTFY_TOKEN)
#   - dostęp do ~/Code/gstarcad-ai/
#
# Autor: Dawid Jakubowski + Claude (projekt gstarcad-ai)
# Wersja: 1.0 (2026-06-30)

set -euo pipefail

# ---------------------------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------------------------
REPO_PATH="${HOME}/Code/gstarcad-ai"
DATE_TODAY=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%A)
REPORT_FILE="${REPO_PATH}/przeglady/${DATE_TODAY}-przeglad.md"
NTFY_TOPIC="https://ntfy.init3.pro/gstarcad-ai-przeglad"
LOG_FILE="${HOME}/Library/Logs/pro.init3.tygodniowy-przeglad-gstarcad.log"

# ---------------------------------------------------------------------------
# Załaduj zmienne środowiskowe (per feedback_init3_env_loader)
# ---------------------------------------------------------------------------
if [ -f "${HOME}/.config/init3/load-env.sh" ]; then
    # shellcheck source=/dev/null
    source "${HOME}/.config/init3/load-env.sh"
else
    echo "[$(date)] OSTRZEŻENIE: brak load-env.sh, kontynuuję bez NTFY_TOKEN" >> "${LOG_FILE}"
fi

# ---------------------------------------------------------------------------
# Funkcja: zapis do dziennika
# ---------------------------------------------------------------------------
log() {
    echo "[$(date +%H:%M:%S)] $*" >> "${LOG_FILE}"
}

log "=========================================="
log "Start procedury nadzorczej (${DATE_TODAY}, ${DAY_OF_WEEK})"
log "=========================================="

# ---------------------------------------------------------------------------
# Krok 1: pobierz świeży stan repozytorium
# ---------------------------------------------------------------------------
cd "${REPO_PATH}" || { log "BŁĄD: brak ${REPO_PATH}"; exit 1; }

log "Pobieram świeże dane z origin..."
git fetch origin main > /dev/null 2>&1
git pull origin main > /dev/null 2>&1

# ---------------------------------------------------------------------------
# Krok 2: zbierz statystyki zadań
# ---------------------------------------------------------------------------
log "Analizuję pliki zadań w tasks/..."

TASKS_TOTAL=0
TASKS_OCZEKUJE=0
TASKS_W_TRAKCIE=0
TASKS_ZAKONCZONE=0

# Iteruj po wszystkich plikach T-*.md
for task_file in "${REPO_PATH}"/tasks/T-*.md; do
    [ -f "${task_file}" ] || continue
    TASKS_TOTAL=$((TASKS_TOTAL + 1))

    # Wyszukaj linię ze statusem (np. "| Status | oczekuje |")
    status_line=$(grep -i "^| Status" "${task_file}" || echo "")

    if echo "${status_line}" | grep -qi "oczekuje"; then
        TASKS_OCZEKUJE=$((TASKS_OCZEKUJE + 1))
    elif echo "${status_line}" | grep -qi "w trakcie"; then
        TASKS_W_TRAKCIE=$((TASKS_W_TRAKCIE + 1))
    elif echo "${status_line}" | grep -qi "zakończone\|wykonane"; then
        TASKS_ZAKONCZONE=$((TASKS_ZAKONCZONE + 1))
    fi
done

# ---------------------------------------------------------------------------
# Krok 3: zbierz zatwierdzenia z ostatnich 7 dni
# ---------------------------------------------------------------------------
log "Czytam git log z ostatnich 7 dni..."

COMMIT_COUNT=$(git log --since="7 days ago" --oneline | wc -l | tr -d ' ')
COMMITS_LIST=$(git log --since="7 days ago" --pretty=format:"- %h %s (%an, %ar)" 2>/dev/null || echo "(brak)")

# ---------------------------------------------------------------------------
# Krok 4: oceń tempo
# ---------------------------------------------------------------------------
# Reguły kciuka:
#   - 0 zatwierdzeń przez tydzień = mizerne
#   - 1-3 zatwierdzenia = średnie
#   - 4 i więcej = dobre
if [ "${COMMIT_COUNT}" -eq 0 ] && [ "${TASKS_W_TRAKCIE}" -eq 0 ]; then
    WERDYKT="mizerny"
    WERDYKT_EMOJI="🔴"
elif [ "${COMMIT_COUNT}" -le 3 ]; then
    WERDYKT="średni"
    WERDYKT_EMOJI="🟡"
else
    WERDYKT="dobry"
    WERDYKT_EMOJI="🟢"
fi

# ---------------------------------------------------------------------------
# Krok 5: wygeneruj raport
# ---------------------------------------------------------------------------
log "Generuję raport: ${REPORT_FILE}"

cat > "${REPORT_FILE}" <<EOF
# Raport cotygodniowy projektu gstarcad-ai

**Data raportu:** ${DATE_TODAY} (${DAY_OF_WEEK})
**Generowane automatycznie przez procedurę pro.init3.tygodniowy-przeglad-gstarcad**
**Werdykt:** ${WERDYKT_EMOJI} **${WERDYKT}**

## Co się stało w ostatnim tygodniu

**Liczba zatwierdzeń w git:** ${COMMIT_COUNT}

### Lista zatwierdzeń:

${COMMITS_LIST}

## Stan zadań

| Status | Liczba |
|---|---|
| Razem zadań | ${TASKS_TOTAL} |
| Oczekuje | ${TASKS_OCZEKUJE} |
| W trakcie | ${TASKS_W_TRAKCIE} |
| Zakończone | ${TASKS_ZAKONCZONE} |

## Ocena tempa

EOF

# Dynamiczna ocena
case "${WERDYKT}" in
    "dobry")
        cat >> "${REPORT_FILE}" <<EOF
Tempo prac w ostatnim tygodniu jest dobre. Co najmniej cztery zatwierdzenia oznaczają, że zespół faktycznie pracuje. Zadania przesuwają się ze stanu „oczekuje" przez „w trakcie" do „zakończone". Sugeruję utrzymać kierunek bez interwencji.
EOF
        ;;
    "średni")
        cat >> "${REPORT_FILE}" <<EOF
Tempo prac w ostatnim tygodniu jest średnie. Trzy lub mniej zatwierdzeń wskazuje na powolny ruch — może to być chwilowy zaczep, ale jeśli się powtórzy w przyszłym tygodniu, warto przejrzeć, które zadania się zacięły. Sugeruję: krótka rozmowa z osobami przypisanymi do zadań w stanie „w trakcie", żeby zorientować się, czy nie potrzebują pomocy.
EOF
        ;;
    "mizerny")
        cat >> "${REPORT_FILE}" <<EOF
**Tempo prac w ostatnim tygodniu jest mizerne.** Brak zatwierdzeń przez cały tydzień plus brak zadań w stanie „w trakcie" oznacza, że projekt utknął. Sugeruję:

1. Sprawdzić, czy ktoś z zespołu nie jest chory albo na urlopie (jeśli tak — to wyjaśnia stan i nie wymaga interwencji)
2. Jeśli nie — bezpośrednio porozmawiać z osobami przypisanymi do oczekujących zadań i zorientować się, co jest blokerem
3. Jeśli bloker jest typu „nie wiem jak zacząć" — przekazać do Claude'a przez Dawida w sesji pomocy
EOF
        ;;
esac

cat >> "${REPORT_FILE}" <<EOF

## Następny raport

Następny raport zostanie wygenerowany automatycznie w piątek $(date -v +7d +%Y-%m-%d).

---

*Procedura cotygodniowego nadzoru: pro.init3.tygodniowy-przeglad-gstarcad. Wersja: 1.0. Repozytorium: https://github.com/init3-sentry/gstarcad-ai*
EOF

# ---------------------------------------------------------------------------
# Krok 6: zatwierdź raport i wypchnij
# ---------------------------------------------------------------------------
log "Zatwierdzam i wypycham raport..."

cd "${REPO_PATH}"
git add "przeglady/${DATE_TODAY}-przeglad.md"
git commit -m "Cotygodniowy raport nadzorczy: ${DATE_TODAY} (werdykt: ${WERDYKT})

Generowane automatycznie przez procedurę pro.init3.tygodniowy-przeglad-gstarcad.
Werdykt: ${WERDYKT_EMOJI} ${WERDYKT}
Zatwierdzenia w git w ostatnim tygodniu: ${COMMIT_COUNT}
Zadań razem: ${TASKS_TOTAL} (oczekuje: ${TASKS_OCZEKUJE}, w trakcie: ${TASKS_W_TRAKCIE}, zakończone: ${TASKS_ZAKONCZONE})

Co-Authored-By: pro.init3.tygodniowy-przeglad-gstarcad <noreply@init3.pro>" > /dev/null 2>&1 || log "OSTRZEŻENIE: brak zmian do zatwierdzenia (raport już istnieje?)"

git push origin main > /dev/null 2>&1 || log "OSTRZEŻENIE: nie udało się wypchnąć zmian"

# ---------------------------------------------------------------------------
# Krok 7: wyślij powiadomienie push przez ntfy
# ---------------------------------------------------------------------------
log "Wysyłam powiadomienie push do ${NTFY_TOPIC}..."

if [ -n "${NTFY_TOKEN:-}" ]; then
    curl -s \
        -u ":${NTFY_TOKEN}" \
        -H "Title: gstarcad-ai: raport ${DATE_TODAY}" \
        -H "Priority: default" \
        -H "Tags: clipboard" \
        -d "Werdykt: ${WERDYKT_EMOJI} ${WERDYKT}. Zatwierdzeń w git: ${COMMIT_COUNT}. Zadań w trakcie: ${TASKS_W_TRAKCIE}, zakończonych: ${TASKS_ZAKONCZONE}. Pełen raport w repozytorium." \
        "${NTFY_TOPIC}" > /dev/null
    log "Powiadomienie wysłane."
else
    log "BRAK NTFY_TOKEN — pominięto powiadomienie push."
fi

log "Procedura zakończona pomyślnie."
log "=========================================="
exit 0
