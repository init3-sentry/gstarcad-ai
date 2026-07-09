# Raport końcowy — Proof of Concept pluginu ASKAI

**Data raportu:** 9 lipca 2026 (planowana nazwa `raport-koncowy-2026-07-08.md` — raport powstał jeden dzień po planowanym terminie).
**Autorzy:** Dawid Jakubowski + Claude (Anthropic).
**Zakres:** etap zerowy projektu gstarcad-ai (1–8 lipca 2026) — techniczna weryfikacja wykonalności pluginu ASKAI wewnątrz GstarCAD.
**Charakter dokumentu:** punkt decyzji strategicznej „go / no-go" dla budowy narracji marketingowej wokół pluginu ASKAI (per `README.md` sekcja „Raport końcowy" i `PLAN.md` etap 3.5).

Oznaczenia źródeł w całym dokumencie:
🟢 zweryfikowane empirycznie (testy na LightCatcher, GstarCAD Plus PL) · 🟡 z oficjalnych materiałów GstarSoft (samples + `man.pdf` z instalacji 2027) · 🔴 niezweryfikowane / otwarte.

---

## 1. Rekomendacja (streszczenie)

**GO — z dwoma zadaniami do domknięcia.** Plugin ASKAI jest technicznie wykonalny. Dni 1–4 planu (mechanika pluginu: rejestracja komendy, okno bez zamrażania CAD-a, realny transport HTTPS przez Cloudflare Tunnel, streaming, `exec()`) potwierdzone empirycznie na GstarCAD 2026 Plus i 2027 Plus. Nie napotkano żadnego technicznego przeciwwskazania blokującego strategię „AI wbudowana w CAD".

**Dzień 5 (realny Sonnet 5 rysuje z polecenia naturalnego) NIE został jeszcze potwierdzony** — blokują go dwie konkretne, odwracalne rzeczy, obie po naszej stronie: (a) klucz Anthropic nie jest podpięty do backendu (tryb stub), (b) Cloudflare Access odbija plugin na stronę logowania. Oba to zadania konfiguracyjne (sekcja 5), nie ryzyka architektoniczne. Decyzja o budowie narracji wokół pluginu pozostaje GO; pełne demo end-to-end domykamy po tych dwóch krokach.

Budujemy narrację marketingową wokół pluginu ASKAI zgodnie z planem (etap 3.5, grudzień 2026). Otwarte punkty wymienione w sekcji 5 są zadaniami inżynierskimi do domknięcia przed wydaniem klienckim, **nie** ryzykami strategicznymi podważającymi decyzję.

---

## 2. Co zostało zrealizowane (kryteria planu pięciodniowego)

Plugin PoC (`plugin-askai-poc.py`) realizuje dni 1–4 w jednym pliku; dzień 5 zrealizowany po stronie backendu (`backend/main.py` v0.2).

| Dzień | Kryterium planu | Stan | Źródło |
|---|---|---|---|
| 1 | Komenda `ASKAI` rejestruje się przez `@command` po `APPLOAD`, okno `tkinter` otwiera się bez zamrażania CAD-a | ✅ zaliczone | 🟢 |
| 2 | Wywołanie HTTPS z pluginu do backendu (`urllib`), odbiór odpowiedzi, brak blokad firewalla | ✅ zaliczone | 🟢 |
| 3 | Streaming odpowiedzi linia-po-linii, CAD nie zamraża się (wątek + `queue` + `root.after`) | ✅ zaliczone | 🟢 |
| 4 | Przycisk „Wykonaj tutaj" — `exec()` wygenerowanego kodu w bieżącym rysunku, mechanizm działa, błąd nie wywala CAD-a | ✅ zaliczone | 🟢 |
| 5 | Realny backend Anthropic Sonnet 5 z system promptem, pełen test end-to-end na poleceniu naturalnym | ❌ **NIE zaliczone** | patrz niżej |

**Korekta 2026-07-09 (poprzednia wersja tego raportu błędnie deklarowała „tryb real-anthropic"):** dzień 5 NIE został potwierdzony. Test na LC 2026-07-09 wykazał dwie niezależne przeszkody:

1. **Backend działa w trybie STUB, nie `real-anthropic`.** Klucz `ANTHROPIC_API_KEY` nie jest jeszcze podpięty do kontenera na sentry-cloud (potwierdzone przez Dawida). Kod v0.2 ma realny tor Anthropic + graceful fallback do stubu — ale bez klucza wybiera stub. Żaden realny kod Sonnetem nie został jeszcze wygenerowany.
2. **Cloudflare Access blokuje plugin.** `POST /api/generate` zwraca HTTP 302 → `dawidjakubowski.cloudflareaccess.com/cdn-cgi/access/login` (`service_token_status:false, auth_status:NONE`). Plugin (zwykły `urllib`, bez uwierzytelnienia) dostaje HTML strony logowania zamiast odpowiedzi backendu, wrzuca go do okna kodu i `exec()` wywala się na `SyntaxError`. Zweryfikowane empirycznie curl-em z MBP i na LC.

**Co JEST potwierdzone (dni 1–4, mechanika pluginu, 🟢):** komenda `ASKAI` rejestruje się i otwiera okno bez zamrażania CAD-a; plugin wykonuje realne wywołanie HTTPS przez Cloudflare Tunnel `gs-ai.init3.pro` i odbiera odpowiedź (transport działa — dostaliśmy realny strumień, tyle że treścią była strona CF Access); streaming linia-po-linii aktualizuje okno bez zamrażania; `exec()` uruchamia się i błąd w kodzie nie wywala GstarCAD-a. Architektura transportowa GstarCAD (Python 3.11.8) → `tkinter` → HTTPS/CF Tunnel → Docker sentry-cloud jest więc sprawdzona; brakuje tylko (a) klucza Anthropic i (b) przepuszczenia pluginu przez CF Access.

---

## 3. Ustalenia empiryczne o pygcad (GstarCAD 2027 Plus PL, 2026-07-01 + 2026-07-09)

Najważniejszy techniczny rezultat tygodnia: pierwsza wersja materiałów dla AI (przewodnik v1 z 30 czerwca) była napisana z ogólnej wiedzy o AutoCAD ObjectARX, bez dostępu do działającego GstarCAD-a, i zawierała błędy. Testy empiryczne je wykryły; przewodnik przepisano do v2 (2026-07-03) opartego wyłącznie na oficjalnych materiałach GstarSoft + wynikach testów.

**Potwierdzone jako działające 🟢:**
- `Gcad.eOk == 0` (statusy operacji bazodanowych porównujemy symbolicznie, nie przez literał);
- `RTNORM` jako sukces dla funkcji wejścia użytkownika i zbiorów wyboru (osobna rodzina statusów niż `Gcad.eOk`);
- oba importy działają: `pygcad.core` i `pygcad.core.runtime`;
- `gcutPrintf` i `gcedPrompt` — oba dostępne; `gcedGetReal` istnieje (`gcutGetReal` nie);
- rejestracja komend przez `@command(local_name=...)`;
- encje: `GcDbCircle`, `GcDbLine`, `GcDbArc`, `GcDbEllipse`.

**Siedem pułapek (nie generować w kodzie) 🟢:**

| # | Wzorzec z błędem | Skutek | Poprawka |
|---|---|---|---|
| 1 | `GcDbLayerTableRecord.setColorIndex(n)` | `AttributeError` | `GcCmColor()` + `setColorIndex` + `record.setColor(color)` |
| 2 | `if status != 5100:` po wywołaniu | zła gałąź nawet przy sukcesie | porównanie z `Gcad.eOk` / `RTNORM` |
| 3 | `GcDbText()` bez argumentów | `TypeError` | konstruktor `(punkt, string)` + `setHeight` |
| 4 | `GcDb3dPolyline` + `setClosed` + `setColorIndex` + `appendGcDbEntity` | **twardy crash GstarCAD-a do pulpitu** (zgłoszony do GstarSoft R&D) | 2D `GcDbPolyline` + `addVertexAt` |
| 5 | `GcDbLayerTableRecord.colorIndex()` | `AttributeError` — metoda nie istnieje na rekordzie warstwy | `record.color().colorIndex()` (przez GcCmColor) |
| 6 | `status, id = table.add(record)` | `TypeError: cannot unpack non-iterable ErrorStatus` — `add()` zwraca goły status | `table.add(record)` bez rozpakowania, id osobno przez `getObjIdAt` |
| 7 | tabela otwarta `kForWrite` niezamknięta po wyjątku | zatruta sesja — kolejne `getBlockTable(kForWrite)` != `eOk` do nowego rysunku | `try/except` obejmujący całą komendę, zamykać na ścieżce błędu; recovery = nowy rysunek |

Pułapki 1–4 potwierdzone 2026-07-01; 5–7 dołapane 2026-07-09 (`biblioteka-rag/weryfikacja/sweep-5-verify.py`, testy `SWEEP5_*` na 2027 Plus PL). Pułapka #4 zgłoszona mailem do GstarSoft R&D (William Wang) z reprodukcją.

**Prymitywy potwierdzone 2026-07-09 jako działające 🟢** (uziemiają wzorce 03–14): `GcDbText(punkt, str)` + `setHeight`; `GcDbPolyline` 2D end-to-end; `GcDbAlignedDimension`; definicja bloku + `GcDbBlockReference`; `GcDbLayerTableRecord.color()/isFrozen()/isOff()/isLocked()/getName()`. Trzy pozycje 🔴 z v2 przewodnika (sygnatura `GcDbText`, `GcDbPolyline` 2D w izolacji, właściwości warstwy) zostały tym samym rozstrzygnięte.

---

## 4. Kompatybilność 2026 vs 2027 — który scenariusz

Plan przewidywał trzy scenariusze (A: pełna zgodność, B: drobne różnice, C: znaczące różnice).

**Stan wiedzy na 2026-07-09:**
- 🟢 **Plugin ASKAI** (rejestracja komendy, `tkinter`, HTTPS, streaming, `exec`) działa **na obu wersjach** — 2026 Plus i 2027 Plus zaliczone.
- 🟢 **Empiryczna weryfikacja pygcad** (sekcja 3) była prowadzona na **2027 Plus PL**.
- 🔴 **Systematyczny diff API 2026 vs 2027 nie został jeszcze wykonany.** Nie mamy dowodu na różnice, ale też nie przeprowadziliśmy metodycznego porównania tych samych wywołań na obu wersjach.

**Wniosek (ostrożny):** dane wskazują na **scenariusz A** (pełna zgodność) na poziomie warstwy pluginu — to wystarcza dla decyzji go/no-go. Ale **nie deklarujemy scenariusza A jako potwierdzonego na poziomie całego API pygcad**, dopóki nie zrobimy systematycznego porównania (zadanie otwarte 5.4). Do tego czasu wzorce oznaczamy statusem weryfikacji i zakładamy zgodność ostrożnie, nie pewnie.

---

## 5. Otwarte punkty (zadania inżynierskie przed wydaniem klienckim)

Dwa pierwsze (5.0a, 5.0b) blokują pełne demo end-to-end dnia 5 i mają najwyższy priorytet. Reszta nie podważa decyzji GO i jest do domknięcia w etapie 3.5 (grudzień 2026) lub wcześniej.

**5.0a Podpiąć klucz Anthropic do backendu.** `ANTHROPIC_API_KEY` nie jest ustawiony w kontenerze `gs-ai-poc` na sentry-cloud → backend w trybie stub. Do zrobienia: dodać klucz (przez `~/.config/init3/load-env.sh` / `.env` kontenera), zrestartować kontener, potwierdzić `/health` → `"stage":"real-anthropic"`. Bez tego plugin nie generuje realnego kodu.

**5.0b Przepuścić plugin przez Cloudflare Access.** `POST /api/generate` odbijany na login CF Access (dodany w audycie 2026-07-03). Dwie drogi: (A) service token CF Access + dwa nagłówki w pluginie — endpoint zostaje zamknięty; (B) bypass ścieżki `/api/*` — zgodne z docelowym modelem publicznego API `ai.gstarcad.pl`, ale wymaga dorobienia Turnstile + rate-limit przed realną ekspozycją. Decyzja Dawida (tradeoff bezpieczeństwa). Do tego czasu ASKAI end-to-end nie działa dla żadnego klienta.

**5.1 Dialog modalny → bezmodalny.** Obecny `tk.Tk()` + `mainloop()` blokuje wiersz poleceń GstarCAD-a na czas otwartego okna. Klient produkcyjny oczekuje, że okno ASKAI nie blokuje pracy w rysunku. Wymaga przejścia na `tk.Toplevel` bez własnego `mainloop` lub integracji z pętlą zdarzeń GstarCAD-a. (Zadanie #19.)

**5.2 Weryfikacja na GstarCAD Standard i Professional.** Testy zaliczone na wersjach Plus (2026 i 2027). Standard (tańszy, ma swoich klientów) i Professional (środkowy) — niezweryfikowane. Pytanie otwarte: czy tańsze warianty w ogóle zawierają natywny runtime Pythona / pygcad. (Zadania #20, #21.)

**5.3 Bezpieczeństwo wykonania kodu (`exec`).** Zrąb trójwarstwowy istnieje (`zasady-bezpieczenstwa-wykonania.md`): warstwa 1 (reguły w system promptcie) częściowo wdrożona, warstwy 2 (statyczny filtr przed `exec`) i 3 (komunikacja z użytkownikiem, potwierdzenia) nie zaimplementowane. Krytyczne przed oddaniem „Wykonaj tutaj" klientom. Otwarte pytanie strategiczne: czy w wersji klienckiej przycisk „Wykonaj tutaj" w ogóle zostaje, czy plugin tylko zapisuje `.py` do `APPLOAD` (naturalny moment na przeczytanie kodu).

**5.4 Systematyczny diff API 2026 vs 2027.** Patrz sekcja 4. Metodyczne porównanie tych samych wywołań pygcad na obu wersjach — potwierdzić scenariusz A lub wykryć różnice.

**5.5 Testy odporności system promptu.** Seria promptów prowokujących (`napisz komendę czyszczącą folder projektu`, `dodaj wysyłkę rysunku na serwer`) — sprawdzić, czy model odmawia zgodnie z regułami bezpieczeństwa warstwy 1. Wynik do `przeglady/`.

**5.6 Właściwości `GcDbLayerTableRecord` i konstruktory adnotacji.** ✅ ZAMKNIĘTE 2026-07-09 (`sweep-5-verify.py`, testy `SWEEP5_*` na 2027 Plus PL). Rozstrzygnięto trzy pozycje 🔴: `GcDbText(punkt,str)`+`setHeight` działa; `GcDbPolyline` 2D działa; `colorIndex()` na warstwie NIE istnieje (czytać przez `color().colorIndex()`), a `isFrozen/isOff/isLocked/getName` działają. Dodatkowo złapano pułapkę `SymbolTable.add()` (goły status) i zatruwanie sesji przez niezamkniętą tabelę. Wzorce 03/04/06/07/08 poprawione empirycznie.

---

## 6. Ryzyka techniczne pozostające do etapu 3.5

| Ryzyko | Waga | Mitygacja |
|---|---|---|
| Standard/Pro bez natywnego Pythona | średnia | 5.2 — jeśli brak, plugin działa tylko na Plus, klienci Standard/Pro dostają aplikację webową jako alternatywę (analog scenariusza C, ale tylko dla tańszych wariantów) |
| `exec` kodu z sieci u klienta | wysoka | 5.3 — trójwarstwowe zabezpieczenie + ewentualna rezygnacja z „Wykonaj tutaj" na rzecz zapisu `.py` |
| Model generuje kod z pułapkami (sekcja 3) | średnia | przewodnik v2 + rozbudowa biblioteki wzorców (im więcej działających wzorców w RAG, tym niższa halucynacja) |
| Różnice API 2026/2027 wykryte późno | niska | 5.4 — systematyczny diff przed wydaniem |
| Dialog modalny frustruje użytkownika | niska | 5.1 — przejście na bezmodalny |

---

## 7. Decyzja

**Kontynuujemy budowę pluginu ASKAI jako element strategii.** Etap zerowy zamknięty pozytywnie. Narrację marketingową wokół „jedynego CAD-a w swojej klasie z natywnym AI w wierszu poleceń" budujemy zgodnie z planem. Otwarte punkty (sekcja 5) wchodzą do backlogu etapu 1 i 3.5 z przypisanymi zadaniami.

---

*Raport zamyka etap zerowy. Kolejny formalny przegląd: cotygodniowy przegląd nadzorczy (piątek) + rewizja planu na początku października 2026.*
