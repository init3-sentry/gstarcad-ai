# Testy stabilności GstarCAD 2027 SP1 — instrukcja dla zespołu

**Wersja:** 1.0 — 10 lipca 2026
**Prowadzi:** Dawid Jakubowski
**Wykonują:** zespół pomocy technicznej (kilka maszyn, różne konfiguracje, niezależnie)

## Po co to robimy (w dwóch zdaniach)

Testowaliśmy plugin AI dla GstarCAD-a zdalnie (przez pulpit zdalny / RDP) i GstarCAD 2027 SP1 wielokrotnie się zawieszał („zamknięcie awaryjne"). Musimy ustalić **czy to wina GstarCAD-a, czy tylko pulpitu zdalnego** — dlatego powtarzamy dokładnie te same testy **lokalnie, przy maszynie**, na kilku komputerach. Wynik decyduje o dalszych krokach projektu.

## Najważniejsza zmienna: LOKALNIE, nie przez RDP

**Testy rób siedząc PRZY komputerze** (klawiatura i mysz tego komputera), **NIE przez pulpit zdalny / RDP / AnyDesk / TeamViewer.** To jest cały sens tych testów. Jeśli ktoś testuje przez zdalny pulpit — zapisz to wyraźnie w raporcie, bo wynik znaczy wtedy co innego.

## ⚠️ Krok 0 — Python 3.11.8 + PATH (BEZ TEGO NIC NIE ZADZIAŁA)

**Wbrew pozorom pygcad NIE działa od razu po instalacji GstarCAD-a.** Na świeżej maszynie polecenie `APPLOAD` nie zarejestruje żadnej komendy z pliku `.py`, dopóki w systemie nie ma **Pythona 3.11.8 (64-bit) zainstalowanego i dodanego do zmiennej PATH** (potwierdzone empirycznie na maszynie testowej: `C:\Program Files\Python311\` w PATH, `python --version` → `Python 3.11.8`).

**Zrób to PRZED testami:**

1. Zainstaluj **Python 3.11.8 (Windows 64-bit)** — dokładnie ta wersja. Zabezpieczona kopia instalatora (z opisem i sumą kontrolną):
   `tools/python-runtime/python-3.11.8-amd64.exe` w repo, albo raw:
   `https://raw.githubusercontent.com/init3-sentry/gstarcad-ai/main/tools/python-runtime/python-3.11.8-amd64.exe`
2. W instalatorze **zaznacz „Add python.exe to PATH"**. Zalecane: „Install for all users" (jako administrator) → trafi do `C:\Program Files\Python311\`.
3. **Weryfikacja PATH** — otwórz nowy wiersz poleceń (cmd) i wpisz:
   ```
   python --version
   ```
   Musi wypisać `Python 3.11.8`. Jeśli „nie jest rozpoznawane jako polecenie" — Python NIE jest w PATH; dodaj ręcznie `C:\Program Files\Python311\` i `C:\Program Files\Python311\Scripts\` do zmiennej środowiskowej PATH (Ustawienia → Zmienne środowiskowe), zrestartuj GstarCAD.
4. **Zapisz w raporcie**, czy Python był już w PATH, czy trzeba było dodać ręcznie — to ważna informacja o realnym procesie wdrożenia u klienta.

> Uwaga: **to jest oficjalny, udokumentowany wymóg** — potwierdzone w podręczniku pygcad GstarSoftu (`biblioteka-rag/oficjalne-materialy-gstarcad-2027/man.pdf`): „zainstaluj `python-3.11.x-amd64.exe`" + „dodaj ścieżkę python3.11.x do zmiennej PATH, zrestartuj GstarCAD". Wcześniej zakładaliśmy błędnie, że GstarCAD ma Pythona „wbudowanego, bez konfiguracji" — to nieprawda. pygcad korzysta z **systemowego** Pythona 3.11.x na PATH.

## Krok 1 — właściwa wersja GstarCAD

„Właściwa wersja" oznacza samą aplikację GstarCAD:

1. **GstarCAD 2027 PL** zainstalowany (standardowy instalator TMSys — ten, którego używamy u klientów).
2. **Nałożony patch SP1:** `GstarCAD2027PL_Patch_SP1_x64.exe`
   Pobranie: `https://ovsdownload.gstarcad.net/software/GstarCAD/2027/PL/GstarCAD2027PL_Patch_SP1_x64.exe`
   (Zamknij GstarCAD, uruchom patch, przejdź przez instalator.)
3. **Weryfikacja wersji:** GstarCAD → menu **Pomoc → O programie**. Powinno być **R27.1.0.2606** (SP1) i edycja (Premium / Standard / Professional). **Zapisz dokładnie co widzisz** — to idzie do raportu.

> Jeśli masz maszynę bez SP1 (samo 2027) — też przetestuj i **wyraźnie zaznacz „bez SP1"**. Porównanie SP1 vs bez SP1 jest cenne.

## Krok 1b — włącz obsługę Pythona w GstarCAD (menedżer aplikacji)

Po zainstalowaniu GstarCAD-a Python **nadal nie zadziała**, dopóki nie włączysz modułu w samym programie:

1. W linii poleceń GstarCAD wpisz komendę **`APPMANAGER`** i Enter — otworzy się **Menedżer aplikacji** (okno z przełącznikami modułów). (Alternatywnie z menu: Aplikacje → Menedżer aplikacji; oryg. chiński z podręcznika: `应用软件 → 应用管理器`.)
2. Znajdź pozycję **„Interfejs Python"** (oryg. `python二次开发接口`) — to jest ten wiersz z przełącznikiem.
3. **Przestaw przełącznik na ON** (zielony) — status ma pokazywać **„Uruchomione"**.
4. Jeśli trzeba — zrestartuj GstarCAD.

> Podpowiedź: gdy moduł jest włączony, wiersz „Interfejs Python" ma zielony przełącznik i status „Uruchomione" (u nas: wersja modułu 1.0.1, 26.5 MB).

> **Zanotuj w raporcie:** dokładną nazwę menu i przełącznika w polskiej wersji (weryfikujemy oficjalne nazewnictwo), oraz czy moduł był domyślnie włączony czy trzeba było go włączyć ręcznie.
>
> Objaw braku tego kroku: `APPLOAD` ładuje plik „z sukcesem", ale komendy (np. `DIAG_INFO`) zgłaszają „nieznane polecenie", albo pojawia się „python接口模块初始化失败 / Python interface module initialization failed".

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
