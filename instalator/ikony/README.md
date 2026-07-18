# Ikony — brief dla grafików

**Wersja z 18.07.2026, po sprawdzeniu na Windows.** Poprzednia wersja opisywała mechanizm macOS
i była w połowie błędna — nie używać.

## Co zamówić

**To jest pewne i nie zależy od tego, jak ostatecznie dostarczymy pliki do GstarCAD.**

| | |
|---|---|
| Format | **rastry** — PNG albo BMP. ⛔ **NIE SVG** |
| Rozmiary | **16, 24, 32, 40, 48, 64 px** — komplet, każdy osobno |
| Głębia | **32 bity z kanałem alfa** (przezroczystość) |
| Warianty | **dwa pełne komplety: jasny i ciemny** |

Czyli na jedno narzędzie: **12 plików** (6 rozmiarów × 2 warianty).

**Dlaczego nie SVG:** na Windows GstarCAD nie obsługuje SVG w interfejsie w żadnym wariancie —
formatu nie ma nawet na wewnętrznej liście obsługiwanych rozszerzeń. Katalog z plikami SVG istnieje
wyłącznie w wersji macOS.

**16 px to osobny rysunek, nie pomniejszony 32.** Producent rysuje mniejsze rozmiary od nowa,
z mniejszą liczbą szczegółów. Przeskalowanie 64 → 16 daje papkę.

Jeśli grafik pracuje w wektorach — dobrze, ale **eksport do tych sześciu rozmiarów musi być częścią
zamówienia**, nie naszą robotą później.

## Nazewnictwo

Nazwa pliku to **tożsamość ikony** — po niej GstarCAD ją znajduje. Dla narzędzia o komendzie
`GSAI_IMPORTXYZ` nazwą jest **`GSAI_IMPORTXYZ`**, bez żadnych przedrostków.

Przedrostek `RCDATA_16_` / `RCDATA_32_`, który widać w plikach producenta, **dokłada GstarCAD sam** —
to jego sposób powiedzenia „weź rozmiar 16 z tej grupy". Grafik o tym nie musi wiedzieć; nazwy
plików nadamy przy pakowaniu.

Lista komend jest w `../komendy.json`.

## Paleta i styl — bez zmian

Ikony mają wyglądać jak część GstarCAD, nie jak wtyczka doklejona z boku.

| Rola | Jasny | Ciemny | Ile razy u producenta |
|---|---|---|---|
| Szary — geometria, tło, kontur | `#d5d5d5` | `#576273` | 1246 |
| Niebieski — akcent, „co robi narzędzie" | `#1aa0ff` | `#1CA2F6` | 957 |
| Pomarańczowy — ostrzeżenie | `#f7990c` | `#FA8B12` | 188 |
| Czerwony — kasowanie, błąd | `#e04d4d` | `#FF5252` | 112 |
| Zielony — potwierdzenie | `#18ae55` | — | 75 |

**Zasada czytania ikony:** szare = rzecz, na której działamy (dokument, obiekt, warstwa).
Niebieskie = czynność. Dlatego jedno spojrzenie wystarcza.

Reszta gramatyki: same wypełnienia bez obrysów, margines ~3 px przy 32 px, zaokrąglenia 1 px,
punkt jako kwadrat 3×3.

⚠️ Zestaw producenta **dryfuje** — obok `#1aa0ff` bywa `#18a0ff`, obok `#d5d5d5` bywa `#d8d8d8`.
To ich niedbałość, nie wzorzec. Trzymamy się kolumn wyżej.

---

## Dla nas, nie dla grafika — jak to trafia do GstarCAD

**Droga pewna, przetarta przez producenta:** ikony jako zasoby w bibliotece `.dll`, para jasna
i ciemna. Tak robi **wszystkie 17 nakładek** w tej instalacji, bez wyjątku.

**Dwie drogi tańsze, nieprzetestowane** — jeśli któraś działa, wystarczy kopiować pliki:

1. **`IconFilePath`** — ustawienie w profilu wskazujące katalog
   `…\AppData\Roaming\Gstarsoft\GstarCAD\R27\pl-PL\Support\Icons`. **Katalog istnieje i jest pusty.**
2. **Obrazki w środku paczki `.cuix`** — silnik interfejsu ma metody do wyjmowania bitmap z paczki
   i zna rozszerzenia `bmp`, `png`, `ico`, `rle`.

Obie do sprawdzenia jednym testem przy pulpicie. **Kolejność ma znaczenie ekonomiczne:** kopiowanie
plików kontra dostarczanie podpisanej biblioteki dla każdej wersji GstarCAD to zupełnie inny koszt
utrzymania.

🔴 **Ryzyko, którego nie znaliśmy:** w manifeście nakładki producenta **biblioteka ikon nie jest
w ogóle zadeklarowana** — wymieniony jest tylko moduł `.grx` i plik `.cuix`. Nie wiadomo, czy silnik
sam przeszukuje wczytane moduły, czy to moduł rejestruje swoje zasoby. Jeśli to drugie, sama
biblioteka położona obok `.cuix` może nie wystarczyć, **a modułu w C++ nie mamy**.

Pełne ustalenia: `gstarcad-ai-wewnetrzne/referencje/` oraz raport `Z-13-ikony-windows.md`.
