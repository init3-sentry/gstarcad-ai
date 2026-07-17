# Instalator — interfejs naszych narzędzi w GstarCAD

## Co to robi

`gsai-cuix-gen.py` czyta `komendy.json` i składa `gsai.cuix` — plik, który wnosi
do GstarCAD **zakładkę na wstążce, menu klasyczne i pasek narzędzi naraz**, z tych
samych danych.

```bash
python3 gsai-cuix-gen.py                    # -> gsai.cuix
python3 gsai-cuix-gen.py --wypakuj podglad  # + rozpakowany XML do obejrzenia
```

Żeby dodać narzędzie do interfejsu — dopisz pozycję w `komendy.json`. Kodu nie ruszasz.

## Dlaczego to jest ważne

Dotychczasowe nakładki na GstarCAD dodają ikony **tylko w widoku klasycznym**, a domyślny
interfejs jest wstążkowy. Rozebranie `express.cuix` producenta pokazało, że **wstążka
jest osiągalna** — ich własny Express Tools wnosi ją dokładnie tym samym mechanizmem
(1 zakładka, 9 paneli, 108 przycisków).

Nasz `gsai.cuix` jest **tym samym rodzajem obywatela co `express.cuix`** — nie wtyczką
doklejoną z boku, tylko modułem wniesionym tą samą drogą, którą producent wnosi swoje.

Pełna anatomia formatu: `gstarcad-ai-wewnetrzne/referencje/cuix-anatomia.md`.

## Dwa niezależne mechanizmy instalatora

| Wnosi | Czym | Stan |
|---|---|---|
| Pythona i komendy `GSAI_*` | Zestaw Startowy (wpis w rejestrze) | czeka na sondę Z-14 |
| Wstążkę, menu, pasek, ikony | **ten `.cuix`** | ✅ generuje się |

Oba bez GUI i bez uruchamiania GstarCAD.

## 🔴 Czego jeszcze nie wiemy

Plik **generuje się poprawnie, ale nie był uruchomiony w GstarCAD.** „Skrypt nie wywalił
się" to nie jest dowód. Trzy pytania czekają na maszynę z Windows (Z-13, Issue #36):

1. **Czy nasz `.cuix` może wnieść własne ikony**, czy SVG trzeba dołożyć do katalogu
   `RibbonIcon/` producenta. To rozstrzyga, co instalator kopiuje i gdzie.
2. **Czy `^C^C_` działa przed naszą komendą.** Podkreślnik wymusza angielską nazwę komendy
   *wbudowanej*; nasze są rejestrowane przez `@command` i żadnej przetłumaczonej nazwy nie
   mają. Dlatego `PREFIKS_MAKRA` w generatorze jest stałą do przełączenia jednym znakiem.
3. **Czy Windows ma identyczną strukturę `.cuix`** — rozebrany wzorzec jest z macOS.

Do czasu odpowiedzi: nie wysyłamy tego klientowi.
