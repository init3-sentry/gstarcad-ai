# Katalog narzędzi GstarCAD (TMSys)

> ⚙️ **Plik generowany automatycznie** przez `skrypty/katalog-gen.py` (cron na Oracle). Nie edytuj ręcznie — opis pochodzi z bloku `# @KATALOG` w każdym skrypcie. Ostatnia aktualizacja: **2026-07-14 10:15**. Narzędzi: **6**.


## Geodezja

| Komenda | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `IMPORTXYZ` | Import współrzędnych | Wskazujesz plik z Excela lub Notatnika ze współrzędnymi punktów, a one lądują w rysunku jako punkty z opisami numerów. Koniec ręcznego wstawiania punkt po punkcie. | Wczytanie 300 punktów pomiarowych z pliku od geodety. |

## Ogólne

| Komenda | Narzędzie | Co robi | Przykład |
|---|---|---|---|
| `AUDYTZ` | Audyt osi Z | Znajduje i zaznacza obiekty, które „uciekły" w trzeci wymiar (Z≠0) i psują pomiary w płaskim rysunku — niewidoczne z góry, inaczej nie do znalezienia. Potem prostuje się je poleceniem FLATTEN. | Wykrycie linii z niezerowym Z, które zawyżały pole powierzchni. |
| `EKSPORT_ATRYBUTOW` | Eksport atrybutów do tabeli | Wyciąga wszystkie atrybuty bloków rysunku (z tabelek, stempli, metryk) do pliku CSV do edycji w Excelu. Fundament pod zestawienia i masową edycję danych. | Wyeksportowanie metryk wszystkich pomieszczeń do arkusza. |
| `IMPORT_ATRYBUTOW` | Import atrybutów z tabeli | Wczytuje z powrotem do rysunku wartości atrybutów po edycji w Excelu (dopasowanie po handle i tagu). Domyka round-trip: eksport, poprawki hurtem, import. | Aktualizacja powierzchni w 50 metrykach po przeliczeniu w arkuszu. |
| `RENUMERUJ` | Renumeracja elementów | Automatyczne przenumerowanie atrybutów wg reguły (prefiks + numer startowy + krok, np. P-001, P-002, P-003…). Zamiast poprawiać numery ręcznie, nadajesz je wszystkim naraz. | Ponumerowanie 200 pomieszczeń na rzucie w kilka sekund. |
| `ZAMIEN_TEKST` | Zamiana tekstów hurtem | Znajdź-i-zamień naraz we wszystkich tekstach, mtekstach i atrybutach bloków całego rysunku. Zamiast poprawiać setki opisów ręcznie, zmieniasz np. nazwę inwestycji jednym poleceniem. | Zmiana numeru działki w 200 opisach na rzucie jednym ruchem. |
