# Katalog narzędzi GstarCAD (TMSys)

> ⚙️ **Plik generowany automatycznie** przez `skrypty/katalog-gen.py` (cron na Oracle). Nie edytuj ręcznie — opis pochodzi z bloku `# @KATALOG` w każdym skrypcie. Daty zmian: historia commitów. Narzędzi: **2**.


## Geodezja

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_IMPORTXYZ` | Import współrzędnych | Wskazujesz plik z Excela lub Notatnika ze współrzędnymi punktów, a one lądują w rysunku jako punkty z opisami numerów. Koniec ręcznego wstawiania punkt po punkcie. | Wczytanie 300 punktów pomiarowych z pliku od geodety. |

## Ogólne

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_AUDYTZ` / `GSAI_AUDITZ` | Audyt osi Z | Znajduje i zaznacza obiekty, które „uciekły" w trzeci wymiar (Z≠0) i psują pomiary w płaskim rysunku — niewidoczne z góry, inaczej nie do znalezienia. Potem prostuje się je poleceniem FLATTEN. | Wykrycie linii z niezerowym Z, które zawyżały pole powierzchni. |
