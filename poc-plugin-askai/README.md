# Proof of Concept — Plugin ASKAI dla GstarCAD

**Wersja:** 1.0 — 1 lipca 2026 (start)
**Wykonawcy:** Dawid Jakubowski + Claude (Anthropic)
**Czas planowany:** jeden tydzień (do 8 lipca 2026)
**Środowisko testowe:** osobna maszyna Dawida z systemem Windows, GstarCAD 2026 i 2027 zainstalowane równocześnie

## Cel proof of concept

Techniczne potwierdzenie, że plugin ASKAI dla GstarCAD-a — planowany do wydania w grudniu 2026 jako kluczowy element strategiczny projektu — jest realnie wykonalny. Jest to punkt „go / no-go" dla całej narracji marketingowej wokół tego pluginu.

Zasada: **fail fast, fail cheap**. Jeśli okaże się, że jest jakieś techniczne przeciwwskazanie — dowiadujemy się o tym w pierwszym tygodniu, kiedy koszt zmiany planu jest minimalny.

## Plan pięciodniowy

### Dzień pierwszy — minimalny plugin z komendą ASKAI

- Napisanie skryptu Pythona z dekoratorem `@command`, rejestrującego komendę `ASKAI` w GstarCAD.
- Komenda wyświetla banalne okno dialogowe w bibliotece `tkinter` po wywołaniu z wiersza poleceń GstarCAD.
- Dialog przyjmuje wpisany tekst, zamyka się poprawnie.

**Kryterium zaliczenia dnia:** komenda się rejestruje po `APPLOAD`, dialog otwiera się i zamyka bez zawieszania GstarCAD-a. Testujemy równocześnie w wersji 2026 i 2027 na osobnej maszynie Dawida.

### Dzień drugi — minimalny backend + wywołanie HTTPS z pluginu

- Napisanie na macOS minimalnego serwera HTTP (FastAPI, jedno endpoint) zwracającego sztywny fragment kodu Python jako odpowiedź.
- Rozszerzenie pluginu z dnia pierwszego o wywołanie tego endpointu przez standardową bibliotekę `urllib` z Pythona.
- Odbiór odpowiedzi i wyświetlenie jej w oknie dialogowym.

**Kryterium zaliczenia dnia:** dialog otwiera się, wysyła zapytanie do backendu, otrzymuje sztywną odpowiedź, wyświetla ją w oknie. Brak blokad zapory ogniowej u Dawida. Backend uruchamiany na macOS lub na Oracle wechat-vm (do decyzji).

### Dzień trzeci — streaming odpowiedzi

- Rozbudowa backendu o streamowanie odpowiedzi (Server-Sent Events albo chunked HTTP transfer).
- Rozbudowa pluginu o odbiór strumienia i aktualizację okna dialogowego w czasie rzeczywistym — tekst pojawia się linia po linii.

**Kryterium zaliczenia dnia:** klient widzi tekst wygenerowany progresywnie w oknie tkinter. GstarCAD nie zamraża się w trakcie odbioru. Konieczne poprawne obsłużenie asynchroniczności w tkinter (najczęściej przez `.after()` z pętlą odczytu bez blokowania głównego wątku).

### Dzień czwarty — wykonanie wygenerowanego kodu w bieżącym rysunku

- Rozbudowa pluginu o przycisk „Wykonaj tutaj" pod oknem dialogowym.
- Naciśnięcie przycisku powoduje wykonanie wygenerowanego kodu Pythona bezpośrednio w kontekście bieżącego rysunku GstarCAD — bez konieczności zapisu do pliku i ponownego `APPLOAD`.
- Bezpieczne wykonanie — w oddzielnej przestrzeni nazw, z odpowiednim obsłużeniem wyjątków.

**Kryterium zaliczenia dnia:** klient wpisuje polecenie, otrzymuje kod, klika „Wykonaj tutaj", w bieżącym rysunku pojawiają się obiekty zgodne z poleceniem. Wykonanie nie wywala GstarCAD-a w razie błędu w wygenerowanym kodzie.

### Dzień piąty — podpięcie prawdziwego backendu Anthropic

- Zamiast sztywnego kodu w backendzie, podpięcie prawdziwego wywołania Anthropic Sonnet 5 z systemem promptem z folderu `biblioteka-rag/przewodnik-systemowy.md`.
- Pełen test end-to-end na trzech-pięciu różnych poleceniach.

**Kryterium zaliczenia dnia:** klient wpisuje „narysuj okrąg o promieniu pięć", model generuje działający kod, kod wykonuje się w rysunku, okrąg pojawia się. Powtórzenie testu na pięciu innych poleceniach z Dawidowego doświadczenia klientowskiego.

## Kompatybilność 2026 vs 2027

Wszystkie testy wykonywane RÓWNOCZEŚNIE na obu wersjach. W raporcie końcowym odnotowujemy każdą zidentyfikowaną różnicę w API programistycznym między wersjami — GstarSoft HQ nie dostarczył jeszcze pełnej dokumentacji dla wersji 2027, więc weryfikacja empiryczna jest jedynym sposobem, żeby wiedzieć, na co się przygotować.

Możliwe scenariusze wyników:
- **Scenariusz A** — API pygcad w 2027 jest w pełni kompatybilne z 2026. Piszemy jeden kod, wypuszczamy plugin działający na obu wersjach.
- **Scenariusz B** — API pygcad w 2027 różni się w drobiazgach. Piszemy jeden kod z warunkową obsługą różnic.
- **Scenariusz C** — API pygcad w 2027 różni się znacząco. Rozważamy dwie odrębne wersje pluginu, albo skupiamy się tylko na 2027 (odcinając bazę 2026 od pluginu, ale zostawiając im aplikację webową jako alternatywę).

Wybór scenariusza wpłynie na strategię marketingową premiery wrześniowej.

## Raport końcowy

Na koniec tygodnia (do 8 lipca 2026) w tym folderze pojawia się plik `raport-koncowy-2026-07-08.md` zawierający:

1. Co działa, co nie działa (twarde dane techniczne).
2. Zidentyfikowane różnice między wersjami 2026 i 2027.
3. Ryzyka techniczne pozostające do etapu 3.5 (grudzień 2026).
4. Rekomendacja: kontynuować budowę pluginu ASKAI jako element strategii? Jeśli nie — jaka jest strategia alternatywna?

**Ten raport jest punktem decyzji strategicznej dla projektu.** Bez pozytywnego wyniku PoC nie budujemy marketingowej narracji wokół pluginu ASKAI dla korporacji.

## Zawartość folderu na końcu tygodnia

- `README.md` — ten dokument
- `raport-koncowy-2026-07-08.md` — twardy raport techniczny
- `plugin-askai-poc.py` — końcowy kod pluginu z PoC
- `backend/` — minimalny backend napisany na potrzeby PoC (odrębna aplikacja)
- `dziennik/` — dzienne notatki z testów Dawida (co się udało, co nie, obserwacje)
- `askai-access.json.example` — wzór konfiguracji dostępu przez Cloudflare Access (patrz niżej)

## Konfiguracja dostępu — Cloudflare Access (od v0.2)

Backend `gs-ai.init3.pro` stoi za Cloudflare Access, więc plugin musi się uwierzytelnić. Od wersji 0.2 (`plugin-askai-poc.py`) plugin wysyła parę nagłówków **service tokenu**: `CF-Access-Client-Id` + `CF-Access-Client-Secret`. Dzięki temu dobija się do backendu **z dowolnej sieci** (także u klienta), a nie tylko z whitelistowanych IP biura.

**Skąd plugin bierze wartości** (kolejność):
1. Zmienne środowiskowe `CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET`.
2. Plik `askai-access.json` **obok** `plugin-askai-poc.py` (wzór: `askai-access.json.example`).

Bez konfiguracji plugin działa dalej (graceful), ale tylko z sieci objętej bypassem IP (biuro / maszyna testowa).

**Wdrożenie:** skopiuj `askai-access.json.example` → `askai-access.json`, wklej parę service tokenu z Cloudflare Zero Trust → Access → Service credentials. Plik `askai-access.json` jest w `.gitignore` — sekret nie trafia do repo. Po stronie Cloudflare aplikacja `gs-ai PoC` ma politykę `non_identity` (dowolny ważny service token) — patrz `gstarcad-ai-wewnetrzne/infrastruktura/gs-ai-access-bypass.sh` i mapa infry.

---

*Plik startowy PoC. Kolejne pliki dochodzą w miarę postępu prac.*
