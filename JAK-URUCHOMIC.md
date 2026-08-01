# Jak uruchomić nasze narzędzia w GstarCAD — krok po kroku

> **To jest jedyna obowiązująca instrukcja uruchomienia.** Wszystkie repozytoria projektu (zespół, Robert, przyszli współpracownicy) linkują tutaj. Jeśli coś się zmieni — zmienia się **tylko ten plik**.
>
> Pierwsze przejście zajmuje kwadrans. Potem uruchomienie narzędzia to dwa kliknięcia.

---

## Część A — przygotowanie GstarCAD (robi się RAZ)

Narzędzia są napisane w Pythonie. GstarCAD potrafi je uruchamiać, ale potrzebuje Pythona **zainstalowanego w systemie**. Są tu dwie pułapki i obie opisane niżej — odpowiadają za zdecydowaną większość zgłoszeń „u mnie nie działa".

### A1. Zainstalować Python 3.11.8 (64-bit)

**Dokładnie ta wersja.** Inne nie zadziałają — GstarCAD szuka konkretnie jej (`python311.dll`).

Instalator prawdopodobnie **jest już na dysku** — dokłada go instalator GstarCAD. Gdyby go nie było, tu leży nasza kopia (ta sama wersja, ze sprawdzoną sumą kontrolną):

👉 **[python-3.11.8-amd64.exe → Download raw file](tools/python-runtime/python-3.11.8-amd64.exe)** *(24 MB)*

### ⚠️ A2. PATH — pułapka numer jeden

**Na pierwszym ekranie instalatora, na samym dole, jest okienko „Add python.exe to PATH". Trzeba je zaznaczyć.**

Jest **domyślnie odznaczone** i bardzo łatwo je przeoczyć. Bez niego GstarCAD nie znajdzie Pythona i narzędzia po prostu się nie wczytają.

- ☑️ **Add python.exe to PATH** ← zaznaczyć
- potem **Install Now**

### A3. Sprawdzić, że się udało (10 sekund)

1. Klawisz **Windows** → wpisać `cmd` → Enter.
2. Wpisać: `python --version` → Enter.
3. Ma się pokazać: **`Python 3.11.8`**

- ✅ **Pokazało `Python 3.11.8`** → gra, dalej.
- ❌ **Co innego albo „nie jest rozpoznane jako polecenie"** → PATH nie zadziałał. Patrz **Ratunek**.

### 🔧 Ratunek — gdy PATH nie zadziałał

**Najprościej:** odinstalować Pythona (Panel sterowania → Programy) i zainstalować ponownie, tym razem **z zaznaczonym** „Add python.exe to PATH". To szybsze niż grzebanie w ustawieniach.

**Gdyby przeinstalowanie odpadało** — da się dopisać ręcznie:

1. Klawisz **Windows** → wpisać `zmienne środowiskowe` → **„Edytuj zmienne środowiskowe systemu"**.
2. Przycisk **„Zmienne środowiskowe…"** (na dole).
3. W dolnej tabeli **„Zmienne systemowe"** znaleźć **`Path`** → zaznaczyć → **Edytuj**.
4. **Nowy** → wkleić ścieżkę do Pythona. Zwykle jedna z dwóch:
   - `C:\Program Files\Python311\`
   - `C:\Users\<nazwa użytkownika>\AppData\Local\Programs\Python\Python311\`
5. **Nowy** ponownie → ta sama ścieżka z `Scripts\` na końcu, np. `C:\Program Files\Python311\Scripts\`
6. **OK** we wszystkich oknach.
7. **Zamknąć i otworzyć GstarCAD** (musi zobaczyć nowe ustawienia).
8. Sprawdzić ponownie: `cmd` → `python --version`

### ⚠️ A4. Włączyć moduł Pythona w GstarCAD — pułapka numer dwa

Moduł jest **fabrycznie wyłączony**. Włącza się raz:

- w GstarCAD wpisać **`APPMANAGER`** → znaleźć na liście **„Interfejs Python"** → przełączyć na włączony (status **„Uruchomione"**).

**Gotowe.** Od tej pory GstarCAD uruchamia nasze narzędzia.

---

## Część B — uruchomienie narzędzia

### B1. Pobrać plik

**Najpewniej — wszystko naraz:** zielony przycisk **Code → Download ZIP**, potem rozpakować. Jeden plik, nic nie psuje się po drodze.

**Pojedynczy plik:** w **[katalogu narzędzi](NARZEDZIA.md)** przy każdym narzędziu jest link. Kliknięcie otwiera stronę pliku → przycisk **„Download raw file"** (strzałka w dół, prawy górny róg).

> ✅ **Sprawdź, że pobrało się DOBRZE:** otwarty plik ma zaczynać się od `#` (to kod). Jeśli w środku widać `<!DOCTYPE html>` / wygląda jak strona internetowa, albo zapisało się jako **`.txt`/`.html`** — to **nie jest narzędzie, tylko strona www**. Wtedy: prawy-klik na „Download raw file" → **„Zapisz element docelowy jako"** i wymuś końcówkę **`.py`**.
> Jak dalej nie idzie — **napisz do nas, dostarczymy plik bezpośrednio** (z sumą kontrolną do sprawdzenia). Nie walcz z przeglądarką.

### B2. Wczytać do GstarCAD

**`APPLOAD`** → wskazać pobrany plik → **„Załadowano z sukcesem"**.

### B3. Uruchomić

Wpisać **nazwę komendy** (WIELKIMI literami, z [katalogu](NARZEDZIA.md)) i Enter.

> **Komendy mają przedrostek `GSAI_`** — czyli `GSAI_IMPORTXYZ`, nie `IMPORTXYZ`. Zmiana z 14.07.2026, żeby nasze narzędzia nie myliły się z komendami GstarCAD. Starsze nazwy (bez przedrostka) już nie działają.

---

## Pierwsza próba na rozgrzewkę — import współrzędnych

1. Pobrać **[25_import_coordinates.py](biblioteka-rag/przyklady/25_import_coordinates.py)** → `APPLOAD`
2. Pobrać przykładowe dane: **[wspolrzedne_excel_pl.csv](biblioteka-rag/przyklady/dane-testowe/wspolrzedne_excel_pl.csv)**
3. W GstarCAD wpisać **`GSAI_IMPORTXYZ`**
4. Wskazać pobrany plik `.csv`
5. Format: wpisać **`NrXY`** → Enter
6. Wpisać **`ZOOM`**, potem **`E`** — pojawią się cztery punkty z numerami 1–4

Jeśli tak się stało — środowisko działa i **każde kolejne narzędzie uruchamia się tak samo**.

---

## Gdy coś nie gra

Po `APPLOAD` komenda „nieznana"? To prawie zawsze jedna z dwóch rzeczy — sprawdzać w tej kolejności:

1. **PATH** (A2/A3) → w `cmd` polecenie `python --version` musi pokazać `Python 3.11.8`
2. **Moduł Pythona wyłączony** (A4) → `APPMANAGER` → „Interfejs Python" → „Uruchomione"

Te dwie przyczyny pokrywają większość przypadków. Jeśli to nie wystarczy — kontakt z pomocą techniczną TMSys albo z Dawidem.
