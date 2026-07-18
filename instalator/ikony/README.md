# Ikony — brief dla grafików

**Wersja z 18.07.2026, po sprawdzeniu na Windows.** Poprzednia wersja opisywała mechanizm macOS
i była w połowie błędna — nie używać.

## Co zamówić

**Sprawdzone empirycznie 18.07.2026 na GstarCAD 2027 Windows.**

| | |
|---|---|
| Format | **BMP, 32 bity z kanałem alfa**. ⛔ **NIE SVG** |
| Rozmiary | **16 × 16** i **32 × 32** px |
| Nazwy plików | `<KOMENDA>_16.bmp` i `<KOMENDA>_32.bmp`, np. `GSAI_IMPORTXYZ_16.bmp` |
| Warianty | jasny — ciemny **wstrzymany**, patrz niżej |

Czyli na jedno narzędzie: **2 pliki**. Lista komend jest w `../komendy.json`.

**16 px to osobny rysunek, nie pomniejszony 32.** Producent rysuje mniejszy rozmiar od nowa,
z mniejszą liczbą szczegółów. Przeskalowanie daje papkę.

Jeśli grafik pracuje w wektorach — dobrze, ale **eksport do BMP w obu rozmiarach musi być częścią
zamówienia**, nie naszą robotą później.

### ⏸️ Wariant ciemny — jeszcze nie zamawiać

Producent robi motyw ciemny przez **podmianę całej biblioteki** (`undet.dll` / `undetDark.dll`).
My mamy jedną paczkę i **nie wiemy jeszcze, jak wskazać wariant**. Do rozstrzygnięcia jednym testem.
Zamawianie drugiego kompletu teraz to ryzyko, że trafi do kosza.

**Dlaczego nie SVG:** na Windows GstarCAD nie obsługuje SVG w interfejsie w żadnym wariancie —
formatu nie ma nawet na wewnętrznej liście obsługiwanych rozszerzeń. Katalog z plikami SVG istnieje
wyłącznie w wersji macOS.

## Nazewnictwo — nazwa pliku JEST mechanizmem

GstarCAD znajduje ikonę **wyłącznie po nazwie pliku**, razem z rozszerzeniem. Zła nazwa to przycisk
bez ikony — bez żadnego komunikatu o błędzie.

Dla komendy `GSAI_IMPORTXYZ` pliki nazywają się:

```
GSAI_IMPORTXYZ_16.bmp
GSAI_IMPORTXYZ_32.bmp
```

Uruchomienie `python3 gsai-cuix-gen.py` wypisuje, których plików brakuje — co do znaku. To jest
lista robocza dla grafika, gotowa.

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

✅ **Rozstrzygnięte: ikony jadą w środku pliku `.cuix`.** Generator pakuje je sam — kładziesz pliki
w tym katalogu, uruchamiasz `python3 gsai-cuix-gen.py` i tyle.

Przepis (sprawdzony, trzy warianty testowane naraz):

1. Obrazek BMP w **korzeniu** paczki `.cuix` — podkatalog **nie działa**.
2. W `MenuGroup.cui`: `<SmallImage Name="NAZWA_16.bmp" />` — **z rozszerzeniem**. Sama nazwa bez
   rozszerzenia **nie działa**.
3. W `[Content_Types].xml` wpis `<Default Extension="bmp" ContentType="image/bmp" />`.

**Czego NIE robimy, a robi producent:** wszystkie 17 nakładek w instalacji dostarcza ikony przez
skompilowaną bibliotekę `.dll`, osobno dla każdej wersji. Nam wystarczy jeden plik — bez kodu w C++,
bez podpisywania, bez utrzymania przez lata.

Ślepe tropy, sprawdzone i odrzucone: ustawienie `IconFilePath` z katalogiem `Support\Icons`
(katalog istnieje, jest pusty i **nic z niego nie jest czytane**) oraz ścieżka z podkatalogiem
w paczce.

Pełne ustalenia: `gstarcad-ai-wewnetrzne/referencje/cuix-anatomia.md` §6b.
