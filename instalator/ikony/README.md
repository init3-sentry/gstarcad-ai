# Ikony — brief dla grafików

**Nazwa pliku nie jest opisem. Nazwa pliku JEST mechanizmem.** GstarCAD wiąże ikonę
z przyciskiem wyłącznie przez nazwę pliku. Zła nazwa = przycisk bez ikony, bez żadnego
komunikatu o błędzie.

## Co dostarczyć

Na każde narzędzie **cztery pliki SVG**:

| Ścieżka | Kiedy widoczna |
|---|---|
| `light/RCDATA_16_<KOMENDA>.svg` | motyw jasny, mały przycisk |
| `light/RCDATA_32_<KOMENDA>.svg` | motyw jasny, duży przycisk |
| `dark/RCDATA_16_<KOMENDA>.svg` | motyw ciemny, mały przycisk |
| `dark/RCDATA_32_<KOMENDA>.svg` | motyw ciemny, duży przycisk |

`<KOMENDA>` bierzemy z `komendy.json`, na przykład `GSAI_IMPORTXYZ`. Wielkości liter
nie zmieniamy.

Uruchomienie `python3 gsai-cuix-gen.py` wypisuje, których plików brakuje — co do znaku.

## Gramatyka ich zestawu (zmierzona na 1705 ikonach)

Ikony mają wyglądać jak część GstarCAD, nie jak wtyczka doklejona z boku.

- **Rysunek 16×16 i 32×32 to dwa osobne rysunki.** Ich 16 nie jest pomniejszonym 32 —
  ma mniej szczegółu. Przeskalowanie 32 do 16 daje papkę.
- **Same wypełnienia, zero obrysów.** W całym ich zestawie nie ma ani jednego `stroke`.
- **Margines 3 px** od krawędzi, zaokrąglenia `rx="1"`.
- **Punkt** to zawsze `<rect width="3" height="3" rx="1"/>`.
- **Ostatni element to przezroczysty prostokąt** na całość:
  `<rect id="TPbg" fill="none" width="32" height="32"/>`.
- Grupy nazywają `id="Gray"` i `id="Blue"`.

### Paleta

| Rola | Jasny | Ciemny | Ile razy u nich |
|---|---|---|---|
| Szary — geometria, tło, kontur | `#d5d5d5` | `#576273` | 1246 |
| Niebieski — akcent, „co robi narzędzie" | `#1aa0ff` | `#1CA2F6` | 957 |
| Pomarańczowy — ostrzeżenie | `#f7990c` | `#FA8B12` | 188 |
| Czerwony — kasowanie, błąd | `#e04d4d` | `#FF5252` | 112 |
| Zielony — potwierdzenie | `#18ae55` | — | 75 |

⚠️ **Ich własny zestaw dryfuje** — obok `#1aa0ff` występuje `#18a0ff` (17×), obok
`#d5d5d5` jest `#d8d8d8`. To ich niedbałość, nie wzorzec. **My trzymamy się kolumny wyżej.**

**Zasada czytania ikony:** szare = rzecz, na której działamy (dokument, obiekt, warstwa).
Niebieskie = czynność. Dlatego jedno spojrzenie wystarcza — niebieski mówi „co to robi".

## Status

**Pusto — czekamy na grafikę.** `.cuix` buduje się bez ikon i przyciski działają;
są po prostu puste. To celowe: mechanizm ma być przetestowany, zanim grafika powstanie.
