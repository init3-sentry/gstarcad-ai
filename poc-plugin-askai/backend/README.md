# Backend PoC

## Wersje

- **v0.1 stub** (wdrożone 1 lipca 2026, dzień 2 planu) — sztywny kod pygcad zwracany zawsze, ignoruje prompt. Weryfikacja pipeline strumieniowego end-to-end.
- **v0.2 hybrid** (kod gotowy 1 lipca 2026 wieczorem, deploy po powrocie z testów) — realny model Anthropic Sonnet 5, graceful fallback do stubu jeśli brak klucza. Deploy: patrz [`DEPLOY.md`](DEPLOY.md).

## Gdzie żyje działający backend

Backend proof of concept **nie jest w tym folderze**. Żyje na serwerze `sentry-cloud` (Oracle Cloud Frankfurt, publiczny adres `130.61.116.107`) jako kontener Docker.

Ten folder zawiera **kod źródłowy** (SoT), z którego stawia się produkcyjny backend na sentry-cloud. Zmiany robimy tu w git, potem `scp` na serwer i rebuild.

## Adresy

- **Publiczny endpoint:** `https://gs-ai.init3.pro`
- **Endpointy pluginu:**
  - `GET /health` — status backendu (JSON)
  - `POST /api/generate` — generowanie kodu z odpowiedzią strumieniową
- **Lokalizacja plików na serwerze:** `/opt/gs-ai-poc/` (Dockerfile + docker-compose.yml + main.py + requirements.txt)

## Stan backendu (1 lipca 2026)

Backend obecnie zwraca **sztywny kod Pythona** (stub — dzień 2 planu). Endpoint `/api/generate` ignoruje zawartość `prompt` w request body i strumieniuje ten sam kod za każdym razem. Celem stubu jest weryfikacja pipeline'u strumieniowania end-to-end pomiędzy pluginem w GstarCAD a serwerem, zanim podepniemy realny model Anthropic (planowane na dzień 5 planu PoC).

## Podpięcie realnego modelu Anthropic (dzień 5)

Docelowo `POST /api/generate` będzie:

1. Odbierał `{"prompt": "..."}` w body
2. Ładował system prompt z `biblioteka-rag/przewodnik-systemowy.md`
3. Wywoływał `anthropic.messages.stream()` z modelem Sonnet 5
4. Strumieniował fragmenty Python kodu do klienta tak jak teraz

Klucz Anthropic API ładowany będzie przez `~/.config/init3/load-env.sh` (zgodnie z regułą init3 env loader).

## Runbook infrastrukturalny

Cała konfiguracja routingu (Cloudflare Tunnel `gs-ai.init3.pro` → `localhost:8082` → kontener) opisana jest w:

- `init3-cortex/operations/infra-runbook.md`, sekcja **3. Cloudflare Tunnel routes**, wpis `gs-ai.init3.pro`

Runbook prowadzony jest w prywatnym repozytorium `init3-sentry/init3-cortex`. Nie kopiujemy jego treści tutaj (dedup DRY) — jest jednym miejscem prawdy o infrastrukturze.
