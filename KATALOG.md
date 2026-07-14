# Katalog narzędzi GstarCAD (TMSys)

> Narzędzia rozszerzające GstarCAD o funkcje przydatne w codziennej pracy. Każde: komenda, krótki opis i przykład zastosowania. Liczba narzędzi: **2**.


## Geodezja

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_IMPORTXYZ` | Import współrzędnych | Wskazujesz plik z Excela lub Notatnika ze współrzędnymi punktów, a one lądują w rysunku jako punkty z opisami numerów. Koniec ręcznego wstawiania punkt po punkcie. | Wczytanie 300 punktów pomiarowych z pliku od geodety. |

## Ogólne

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_AUDYTZ` / `GSAI_AUDITZ` | Audyt osi Z | Znajduje i zaznacza obiekty, które „uciekły" w trzeci wymiar (Z≠0) i psują pomiary w płaskim rysunku — niewidoczne z góry, inaczej nie do znalezienia. Potem prostuje się je poleceniem FLATTEN. | Wykrycie linii z niezerowym Z, które zawyżały pole powierzchni. |
