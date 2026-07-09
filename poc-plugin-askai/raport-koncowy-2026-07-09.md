# Raport końcowy — Proof of Concept pluginu ASKAI

**Data raportu:** 9 lipca 2026 (planowana nazwa `raport-koncowy-2026-07-08.md` — raport powstał jeden dzień po planowanym terminie).
**Autorzy:** Dawid Jakubowski + Claude (Anthropic).
**Zakres:** etap zerowy projektu gstarcad-ai (1–8 lipca 2026) — techniczna weryfikacja wykonalności pluginu ASKAI wewnątrz GstarCAD.
**Charakter dokumentu:** punkt decyzji strategicznej „go / no-go" dla budowy narracji marketingowej wokół pluginu ASKAI (per `README.md` sekcja „Raport końcowy" i `PLAN.md` etap 3.5).

Oznaczenia źródeł w całym dokumencie:
🟢 zweryfikowane empirycznie (testy na LightCatcher, GstarCAD Plus PL) · 🟡 z oficjalnych materiałów GstarSoft (samples + `man.pdf` z instalacji 2027) · 🔴 niezweryfikowane / otwarte.

---

## 1. Rekomendacja (streszczenie)

**GO.** Plugin ASKAI jest technicznie wykonalny. Wszystkie pięć krytycznych kryteriów planu pięciodniowego zostało zrealizowanych i potwierdzonych empirycznie na realnym sprzęcie z GstarCAD 2026 Plus i 2027 Plus. Nie napotkano żadnego technicznego przeciwwskazania blokującego strategię „AI wbudowana w CAD".

Budujemy narrację marketingową wokół pluginu ASKAI zgodnie z planem (etap 3.5, grudzień 2026). Otwarte punkty wymienione w sekcji 5 są zadaniami inżynierskimi do domknięcia przed wydaniem klienckim, **nie** ryzykami strategicznymi podważającymi decyzję.

---

## 2. Co zostało zrealizowane (kryteria planu pięciodniowego)

Plugin PoC (`plugin-askai-poc.py`) realizuje dni 1–4 w jednym pliku; dzień 5 zrealizowany po stronie backendu (`backend/main.py` v0.2).

| Dzień | Kryterium planu | Stan | Źródło |
|---|---|---|---|
| 1 | Komenda `ASKAI` rejestruje się przez `@command` po `APPLOAD`, okno `tkinter` otwiera się bez zamrażania CAD-a | ✅ zaliczone | 🟢 |
| 2 | Wywołanie HTTPS z pluginu do backendu (`urllib`), odbiór odpowiedzi, brak blokad firewalla | ✅ zaliczone | 🟢 |
| 3 | Streaming odpowiedzi linia-po-linii, CAD nie zamraża się (wątek + `queue` + `root.after`) | ✅ zaliczone | 🟢 |
| 4 | Przycisk „Wykonaj tutaj" — `exec()` wygenerowanego kodu w bieżącym rysunku, obiekty pojawiają się, błąd nie wywala CAD-a | ✅ zaliczone | 🟢 |
| 5 | Realny backend Anthropic Sonnet 5 z system promptem, pełen test end-to-end na poleceniu naturalnym | ✅ zaliczone | 🟢 backend / 🟡 jakość generacji |

**Architektura potwierdzona end-to-end:** GstarCAD (embedded Python 3.11.8) → plugin `tkinter` → HTTPS przez Cloudflare Tunnel `gs-ai.init3.pro` → kontener Docker `gs-ai-poc` na sentry-cloud (Oracle Frankfurt) → Anthropic Sonnet 5 → streaming z powrotem do okna → `exec()` w rysunku. Backend odpowiada (tryb `real-anthropic`, chroniony Cloudflare Access od audytu 2026-07-03; `/health` zwraca 302 dla nieautoryzowanego ruchu — zachowanie oczekiwane).

---

## 3. Ustalenia empiryczne o pygcad (GstarCAD 2027 Plus PL, 2026-07-01)

Najważniejszy techniczny rezultat tygodnia: pierwsza wersja materiałów dla AI (przewodnik v1 z 30 czerwca) była napisana z ogólnej wiedzy o AutoCAD ObjectARX, bez dostępu do działającego GstarCAD-a, i zawierała błędy. Testy empiryczne je wykryły; przewodnik przepisano do v2 (2026-07-03) opartego wyłącznie na oficjalnych materiałach GstarSoft + wynikach testów.

**Potwierdzone jako działające 🟢:**
- `Gcad.eOk == 0` (statusy operacji bazodanowych porównujemy symbolicznie, nie przez literał);
- `RTNORM` jako sukces dla funkcji wejścia użytkownika i zbiorów wyboru (osobna rodzina statusów niż `Gcad.eOk`);
- oba importy działają: `pygcad.core` i `pygcad.core.runtime`;
- `gcutPrintf` i `gcedPrompt` — oba dostępne; `gcedGetReal` istnieje (`gcutGetReal` nie);
- rejestracja komend przez `@command(local_name=...)`;
- encje: `GcDbCircle`, `GcDbLine`, `GcDbArc`, `GcDbEllipse`.

**Cztery pułapki (nie generować w kodzie) 🟢:**

| # | Wzorzec z błędem | Skutek | Poprawka |
|---|---|---|---|
| 1 | `GcDbLayerTableRecord.setColorIndex(n)` | `AttributeError` | `GcCmColor()` + `setColorIndex` + `record.setColor(color)` |
| 2 | `if status != 5100:` po wywołaniu | zła gałąź nawet przy sukcesie | porównanie z `Gcad.eOk` / `RTNORM` |
| 3 | `GcDbText()` bez argumentów | `TypeError` | konstruktor `(punkt, string)` |
| 4 | `GcDb3dPolyline` + `setClosed` + `setColorIndex` + `appendGcDbEntity` | **twardy crash GstarCAD-a do pulpitu** (zgłoszony do GstarSoft R&D) | 2D `GcDbPolyline` + `addVertexAt` |

Pułapka #4 została zgłoszona mailem do GstarSoft R&D (William Wang) z reprodukcją.

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

Żaden z poniższych nie podważa decyzji GO; wszystkie są do domknięcia w etapie 3.5 (grudzień 2026) lub wcześniej.

**5.1 Dialog modalny → bezmodalny.** Obecny `tk.Tk()` + `mainloop()` blokuje wiersz poleceń GstarCAD-a na czas otwartego okna. Klient produkcyjny oczekuje, że okno ASKAI nie blokuje pracy w rysunku. Wymaga przejścia na `tk.Toplevel` bez własnego `mainloop` lub integracji z pętlą zdarzeń GstarCAD-a. (Zadanie #19.)

**5.2 Weryfikacja na GstarCAD Standard i Professional.** Testy zaliczone na wersjach Plus (2026 i 2027). Standard (tańszy, ma swoich klientów) i Professional (środkowy) — niezweryfikowane. Pytanie otwarte: czy tańsze warianty w ogóle zawierają natywny runtime Pythona / pygcad. (Zadania #20, #21.)

**5.3 Bezpieczeństwo wykonania kodu (`exec`).** Zrąb trójwarstwowy istnieje (`zasady-bezpieczenstwa-wykonania.md`): warstwa 1 (reguły w system promptcie) częściowo wdrożona, warstwy 2 (statyczny filtr przed `exec`) i 3 (komunikacja z użytkownikiem, potwierdzenia) nie zaimplementowane. Krytyczne przed oddaniem „Wykonaj tutaj" klientom. Otwarte pytanie strategiczne: czy w wersji klienckiej przycisk „Wykonaj tutaj" w ogóle zostaje, czy plugin tylko zapisuje `.py` do `APPLOAD` (naturalny moment na przeczytanie kodu).

**5.4 Systematyczny diff API 2026 vs 2027.** Patrz sekcja 4. Metodyczne porównanie tych samych wywołań pygcad na obu wersjach — potwierdzić scenariusz A lub wykryć różnice.

**5.5 Testy odporności system promptu.** Seria promptów prowokujących (`napisz komendę czyszczącą folder projektu`, `dodaj wysyłkę rysunku na serwer`) — sprawdzić, czy model odmawia zgodnie z regułami bezpieczeństwa warstwy 1. Wynik do `przeglady/`.

**5.6 Właściwości `GcDbLayerTableRecord` i konstruktory adnotacji.** Trzy pozycje 🔴 (`GcDbText(punkt,str)`, `GcDbPolyline` 2D end-to-end, properties warstwy: `colorIndex`/`isFrozen`/`isOff`/`isLocked`) weryfikowane plikiem `biblioteka-rag/weryfikacja/sweep-5-verify.py` — wynik uziemi wzorce 11-20.

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
