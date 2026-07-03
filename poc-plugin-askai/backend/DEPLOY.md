# Deploy backendu PoC

Procedura wdrożenia backendu na infrastrukturę produkcyjną jest dokumentem
wewnętrznym — zawiera adresy serwerów, ścieżki i szczegóły konfiguracji,
które nie należą do publicznego repozytorium.

Zespół TMSys: patrz `gstarcad-ai-wewnetrzne/infrastruktura/DEPLOY-backend-poc.md`.

Dla czytelników zewnętrznych: backend to standardowy kontener Docker
(`docker compose up -d --build` z tego katalogu). Wymaga pliku `.env`
z kluczem `ANTHROPIC_API_KEY` (szablon: `.env.example`); bez klucza wstaje
w trybie stub. Wystaw go za dowolnym reverse proxy z TLS.
