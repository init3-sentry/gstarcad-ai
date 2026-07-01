# Deploy backendu v0.2 na sentry-cloud

**Kontekst:** backend PoC żyje w kontenerze Docker w `/opt/gs-ai-poc/` na sentry-cloud (Oracle Frankfurt, `130.61.116.107`). Wersja 0.1 (stub) została wdrożona 1 lipca 2026. Wersja 0.2 dodaje realny model Anthropic z bezpiecznym fallbackiem do stubu — kontener wstaje niezależnie od tego, czy klucz jest ustawiony.

## Kolejność deployu

### 1. Wyślij pliki na sentry-cloud

Z katalogu `~/Code/gstarcad-ai/poc-plugin-askai/backend/` na MBP:

```bash
scp main.py requirements.txt Dockerfile docker-compose.yml system-prompt.md .env.example oracle:/opt/gs-ai-poc/
```

`oracle` to nazwa hosta w `~/.ssh/config` odpowiadająca sentry-cloud.

### 2. Utwórz plik .env z kluczem Anthropic (fizycznie, ręcznie)

Na sentry-cloud:

```bash
ssh oracle
cd /opt/gs-ai-poc
cp .env.example .env
nano .env
# Wklej realny klucz sk-ant-api03-...
# Zapisz i wyjdź
chmod 600 .env
```

Klucz zdobywasz na `https://console.anthropic.com` (organizacja TMSys, twardy limit $200/miesiąc jako protection).

### 3. Rebuild + restart kontenera

```bash
cd /opt/gs-ai-poc
docker compose up -d --build
```

Docker wykryje zmiany w Dockerfile i zbuduje nowy obraz `gs-ai-poc:0.2`. Kontener wstaje ze stubem jeśli klucz jeszcze nie jest — więc nawet niedokończony deploy nie powoduje przestoju.

### 4. Weryfikacja

Lokalnie na sentry-cloud:

```bash
curl -s http://127.0.0.1:8082/health | jq
```

Powinieneś zobaczyć `"stage": "real-anthropic"` i `"model": "claude-sonnet-5"`, jeśli klucz działa. Jeśli `"stage": "stub"`, sprawdź logi:

```bash
docker logs gs-ai-poc --tail 20
```

Z MBP przez Cloudflare Tunnel:

```bash
curl -s https://gs-ai.init3.pro/health | jq
curl -sX POST https://gs-ai.init3.pro/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"narysuj okrąg o promieniu 5"}' | head -20
```

W trybie real powinieneś dostać sensowny kod Pythona wygenerowany przez model, nie sztywny stub.

### 5. Test z pluginu ASKAI w GstarCAD

Po pozytywnym `curl` teście uruchom komendę `ASKAI` w GstarCAD, wpisz naturalne polecenie (np. „narysuj kwadrat 10 na 10 w punkcie (0,0)"), wciśnij `Generuj kod`. Powinien pojawić się realny wygenerowany kod, nie stub. Wciśnij `Wykonaj tutaj` — obiekt powinien się pojawić w rysunku.

## Rollback do stubu

Wystarczy skasować lub zakomentować `ANTHROPIC_API_KEY` w `/opt/gs-ai-poc/.env` i:

```bash
docker compose restart
```

Kontener wraca do trybu stub w 3 sekundy. Brak downtime dla pluginu, tylko odpowiedź zaczyna być sztywna.

## Notatki bezpieczeństwa

- Klucz Anthropic **nigdy** nie trafia do git (`.gitignore` na `.env`).
- Klucz przechowywany jest **wyłącznie** w `/opt/gs-ai-poc/.env` na sentry-cloud, chmod 600.
- CORS w backendzie ograniczony do `https://ai.gstarcad.pl` i `https://gs-ai.init3.pro` — inne origins dostaną odmowę.
- Twardy limit budżetowy `$200/miesiąc` ustaw w Anthropic Console jako podwójne zabezpieczenie.
- Rate limiting na warstwie Cloudflare (przygotowane dla ai.gstarcad.pl frontendu w drugim etapie).
