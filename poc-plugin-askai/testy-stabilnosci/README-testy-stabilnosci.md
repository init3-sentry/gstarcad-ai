# Testy stabilności GstarCAD 2027 SP1 — instrukcja dla zespołu

**Wersja:** 1.0 — 10 lipca 2026
**Prowadzi:** Dawid Jakubowski
**Wykonują:** zespół pomocy technicznej (kilka maszyn, różne konfiguracje, niezależnie)

## Po co to robimy (w dwóch zdaniach)

Testowaliśmy plugin AI dla GstarCAD-a zdalnie (przez pulpit zdalny / RDP) i GstarCAD 2027 SP1 wielokrotnie się zawieszał („zamknięcie awaryjne"). Musimy ustalić **czy to wina GstarCAD-a, czy tylko pulpitu zdalnego** — dlatego powtarzamy dokładnie te same testy **lokalnie, przy maszynie**, na kilku komputerach. Wynik decyduje o dalszych krokach projektu.

## Najważniejsza zmienna: LOKALNIE, nie przez RDP

**Testy rób siedząc PRZY komputerze** (klawiatura i mysz tego komputera), **NIE przez pulpit zdalny / RDP / AnyDesk / TeamViewer.** To jest cały sens tych testów. Jeśli ktoś testuje przez zdalny pulpit — zapisz to wyraźnie w raporcie, bo wynik znaczy wtedy co innego.

## Krok 1 — właściwa wersja GstarCAD

**Pythona NIE instalujemy.** GstarCAD ma wbudowany własny Python (3.11.8) — nic nie trzeba dokładać. „Właściwa wersja" oznacza samą aplikację GstarCAD:

1. **GstarCAD 2027 PL** zainstalowany (standardowy instalator TMSys — ten, którego używamy u klientów).
2. **Nałożony patch SP1:** `GstarCAD2027PL_Patch_SP1_x64.exe`
   Pobranie: `https://ovsdownload.gstarcad.net/software/GstarCAD/2027/PL/GstarCAD2027PL_Patch_SP1_x64.exe`
   (Zamknij GstarCAD, uruchom patch, przejdź przez instalator.)
3. **Weryfikacja wersji:** GstarCAD → menu **Pomoc → O programie**. Powinno być **R27.1.0.2606** (SP1) i edycja (Premium / Standard / Professional). **Zapisz dokładnie co widzisz** — to idzie do raportu.

> Jeśli masz maszynę bez SP1 (samo 2027) — też przetestuj i **wyraźnie zaznacz „bez SP1"**. Porównanie SP1 vs bez SP1 jest cenne.

## Krok 2 — plik testowy

Skopiuj `gstarcad-diag.py` (z tego folderu) na **Pulpit** testowej maszyny.

## Krok 3 — przebieg testu (powtarzaj wielokrotnie)

Dla **każdego** przebiegu:

1. Uruchom GstarCAD.
2. Nowy pusty rysunek (`Ctrl+N`).
3. W linii poleceń wpisz `APPLOAD`, wskaż `Pulpit\gstarcad-diag.py`, **Załaduj**, zamknij okno.
4. Wpisz komendę (patrz tabela niżej) i **czekaj — nic nie klikaj, nie przełączaj okna** aż się skończy albo zawiesi.

### Komendy do przetestowania

| Komenda | Co robi | Ile razy powtórzyć |
|---|---|---|
| `DIAG_INFO` | zapisuje nagłówek (wersja, maszyna, czas) do pliku logu | 1× na starcie |
| `DIAG_VALIDATE` | 15 testów podstawowych operacji (rysowanie, warstwy, bloki, grupy, tekst, wymiar, XData, odczyt) | **min. 5×** (za każdym razem nowy rysunek) |
| `DIAG_STRESS` | tysiące operacji w pętli — sprawdza „czy kumuluje się i pada po czasie" (trwa ~minutę) | **min. 5×** |
| `DIAG_ALL_SAFE` | wszystko powyżej naraz (INFO+VALIDATE+STRESS) | **min. 10×** — to główny test |
| `DIAG_2DPOLY` | podejrzany o crash (konstrukcja polilinii) — **spodziewamy się, że zawiesi na odświeżeniu po komendzie** | **min. 5×** — potwierdzić powtarzalność |

**Zalecany scenariusz na jedną maszynę:**
1. `DIAG_INFO` raz.
2. `DIAG_ALL_SAFE` — 10 razy pod rząd (nowy rysunek za każdym razem). Notuj, czy i po którym przebiegu coś się zawiesi.
3. `DIAG_2DPOLY` — 5 razy. Notuj, czy zawiesza się za każdym razem.
4. **Wariant kontrolny:** za którymś razem podczas `DIAG_STRESS`/`DIAG_ALL_SAFE` **celowo przełącz okno (Alt+Tab) i wróć** — sprawdź, czy to wywołuje zawieszenie (na RDP wywoływało). Zapisz wynik osobno.

## Krok 4 — co i gdzie zapisujemy

Wszystko loguje się automatycznie do pliku:
**`C:\Users\<twój-user>\Desktop\gstarcad-diag-log.txt`**

Ten plik przeżywa nawet „zamknięcie awaryjne do pulpitu" — ostatnia linia pokazuje, na czym program stanął.

Po testach na danej maszynie:
1. **Skopiuj cały plik** `gstarcad-diag-log.txt` (zmień nazwę na `log-<nazwa-maszyny>.txt`).
2. Wypełnij tabelkę raportu (niżej).
3. Odeślij Dawidowi plik logu + tabelkę (Dawid przekaże do analizy).

> Jeśli GstarCAD zawiesi się i pokaże okno „GCAD Error Report" (raport błędu) — **NIE wysyłaj go od razu**, tylko zrób zrzut ekranu i zanotuj. Decyzję o wysyłce do GstarSoft podejmuje Dawid.

## Szablon raportu (wypełnij per maszyna)

```
=== RAPORT STABILNOŚCI — maszyna nr __ ===

Osoba testująca:      ____________________
Data:                 ____________________

--- KONFIGURACJA ---
Nazwa/hostname:       ____________________
Procesor (CPU):       ____________________
Karta graficzna (GPU):____________________
RAM:                  ____________________
Windows (wersja):     ____________________
GstarCAD wersja:      ____________________  (Pomoc > O programie, np. R27.1.0.2606)
Edycja:               Premium / Standard / Professional   (podkreśl)
SP1 nałożony:         TAK / NIE
Licencja:             pełna / trial / dongle   (podkreśl)
TRYB TESTU:           LOKALNIE przy maszynie / przez RDP   (podkreśl — KLUCZOWE)

--- WYNIKI ---
DIAG_VALIDATE (5×):   ile PASS / ile FAIL / ile razy zawiesiło CAD-a? ____________
DIAG_STRESS (5×):     zawiesiło? TAK/NIE, jeśli tak — po której pętli (A/B/C/D) i iteracji? ____________
DIAG_ALL_SAFE (10×):  ile przebiegów czystych / ile z zawieszeniem? ____________
DIAG_2DPOLY (5×):     zawiesza za każdym razem? TAK/NIE. Na komendzie czy po (na odświeżeniu)? ____________
Alt+Tab test:         przełączenie okna wywołuje zawieszenie? TAK/NIE ____________

--- UWAGI ---
(cokolwiek dziwnego: komunikaty, wzorzec zawieszania, po jakim czasie, itp.)
____________________________________________________________
____________________________________________________________

Plik logu w załączeniu: log-________.txt
```

## Jak czytać wynik (dla orientacji)

- **`DIAG_VALIDATE` i `DIAG_STRESS` przechodzą lokalnie na wszystkich maszynach bez zawieszeń** → GstarCAD jest stabilny, zawieszenia zdalne były winą RDP. Zielone światło.
- **`DIAG_VALIDATE`/`DIAG_STRESS` zawieszają CAD-a też lokalnie** → to realny problem SP1, wymaga zgłoszenia do producenta. Czerwone światło.
- **Tylko `DIAG_2DPOLY` zawiesza** (a reszta jest czysta) → to znany, wąski przypadek (konstrukcja polilinii), omijalny w kodzie — nie blokuje projektu.
- **Zawieszenie tylko po Alt+Tab** → problem z przełączaniem okna, prawdopodobnie środowiskowy.

---

*Pytania kieruj do Dawida. Dziękujemy — te dane rozstrzygają kierunek całego projektu.*
