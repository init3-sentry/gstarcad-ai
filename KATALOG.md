# Katalog narzędzi GstarCAD (TMSys)

> Narzędzia rozszerzające GstarCAD o funkcje przydatne w codziennej pracy. Każde: komenda, krótki opis i przykład zastosowania. Liczba narzędzi: **5**.


## Geodezja

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_IMPORTXYZ` | Import współrzędnych | Wskazujesz plik z Excela lub Notatnika ze współrzędnymi punktów, a one lądują w rysunku jako punkty z opisami numerów. Rozpoznaje układ współrzędnych i prostuje kolejność osi. Koniec ręcznego wstawiania punkt po punkcie. | Wczytanie 300 punktów pomiarowych z pliku od geodety. |

## Ogolne

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_WARSTWY` / `GSAI_LAYERREPORT` | Raport warstw | Pokazuje to, czego Menedżer warstw nie pokaże: warstwy puste, które GstarCAD mimo to uważa za używane (te, których PURGE nie sprząta), nazwy różniące się tylko wielkością liter i zderzone konwencje nazewnicze. Całość ląduje w pliku tekstowym, więc da się ją komuś wysłać. Niczego w rysunku nie zmienia. | Przejęty po kimś rysunek z 300 warstwami — sprawdzenie, co da się posprzątać, zanim ktokolwiek zacznie kasować. |

## Ogólne

| Komenda (PL / EN) | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `GSAI_AUDYTZ` / `GSAI_AUDITZ` | Audyt osi Z | Znajduje i zaznacza obiekty, które „uciekły" w trzeci wymiar (Z≠0) i psują pomiary w płaskim rysunku — niewidoczne z góry, inaczej nie do znalezienia. Potem prostuje się je poleceniem FLATTEN. | Wykrycie linii z niezerowym Z, które zawyżały pole powierzchni. |
| `GSAI_CASTPROBE` | Sonda cast (diagnostyka crashu) |  |  |
| `GSAI_DLUGOSC` | Suma długości |  |  |
