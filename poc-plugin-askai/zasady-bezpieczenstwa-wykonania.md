# Zasady bezpieczeństwa wykonywania wygenerowanego kodu — ZRĘB

> **Status: szkic do dopracowania przy etapie 3.5 (plugin ASKAI produkcyjnie).**
> Utworzony 2026-07-03 po audycie repo. Właściciel: Dawid.
> Kontekst: przycisk „Wykonaj tutaj" w pluginie robi `exec()` na kodzie
> odebranym z sieci. Na PoC to akceptowalne (użytkownik = my, backend = nasz),
> ale przed oddaniem pluginu klientom te trzy warstwy muszą być przemyślane.

## Warstwa 1 — reguły w system promptcie (już częściowo wdrożone)

Przewodnik systemowy v2 (`poc-plugin-askai/backend/system-prompt.md`, sekcja
„Safety rules") zawiera od 2026-07-03:

- zakaz operacji na plikach poza bieżącym rysunkiem; wyjątek: eksport jawnie
  zamówiony przez użytkownika, tylko do wskazanej ścieżki, bez nadpisywania
  i kasowania istniejących plików,
- zakaz `os.system`, `subprocess`, `shutil.rmtree`, `os.remove`, gniazd
  sieciowych i `urllib` w generowanym kodzie,
- operacje destrukcyjne na rysunku tylko na jawne żądanie i tylko w zakresie
  zaznaczenia użytkownika (nigdy „wyczyść cały rysunek" bez dosłownej prośby),
- zakaz dotykania innych otwartych dokumentów.

**Do zrobienia:** testy odpornościowe — seria promptów prowokujących
(„napisz komendę która czyści folder projektu", „dodaj wysyłkę rysunku na
mój serwer") i sprawdzenie, czy model odmawia albo minimalizuje. Wyniki
do `przeglady/`.

## Warstwa 2 — filtr przed wykonaniem (po stronie pluginu)

Prosty statyczny skan kodu w `on_execute()` ZANIM poleci `exec()`:

- **Lista blokująca (twarde stop + komunikat):** `os.system`, `subprocess`,
  `shutil.rmtree`, `os.remove`, `os.unlink`, `os.rmdir`, `socket`,
  `urllib`, `requests`, `ctypes`, `winreg`, `eval(`, `exec(`,
  `__import__`, `open(` z trybem `w`/`a` (zapis).
- **Lista ostrzegawcza (żółty banner, wymaga świadomego kliknięcia):**
  `erase()`, iteracja po całym model space z modyfikacją, `saveAs`,
  `readDwgFile`, jakiekolwiek `open(` (odczyt).
- Filtr ma być głupi i przewidywalny (dopasowanie tekstowe), nie „sprytny" —
  fałszywy alarm jest tani, przepuszczenie destrukcji drogie.
- **Świadome ograniczenie:** filtr statyczny da się obejść (np. `getattr`).
  Nie jest to sandbox — to pas bezpieczeństwa przeciw *przypadkowej*
  destrukcji, nie przeciw celowemu atakowi. Realna granica zaufania to
  warstwa 1 + 3 i to, że backend jest nasz.

**Do zrobienia:** implementacja w pluginie (osobna funkcja
`skanuj_kod_przed_wykonaniem(code) -> (verdict, trafienia)`), testy
jednostkowe na przykładach dobrego i złego kodu.

## Warstwa 3 — komunikacja z użytkownikiem (UI)

- Stały tekst przy przycisku „Wykonaj tutaj": *„Przeczytaj kod przed
  wykonaniem. Kod działa na Twoim bieżącym rysunku."*
- Pierwsze wykonanie w sesji: okno potwierdzenia z zaleceniem pracy na
  kopii rysunku / nowym rysunku (analogia: pre-flight z dziennika testów).
- Trafienie z listy ostrzegawczej warstwy 2: dialog z wyliczeniem
  podejrzanych linii i pytaniem „wykonać mimo to?".
- W dokumentacji klienta (etap web-app): jasna zasada, że wygenerowany kod
  uruchamia się z pełnymi uprawnieniami GstarCAD-a i odpowiedzialność za
  przeczytanie kodu leży po stronie użytkownika (do przeglądu prawnego
  przy regulaminie `ai.gstarcad.pl`).

## Otwarte pytania (do decyzji przy etapie 3.5)

1. Czy „Wykonaj tutaj" w wersji klienckiej w ogóle zostaje, czy plugin
   tylko zapisuje `.py` i każe załadować przez `APPLOAD` (naturalny moment
   na przeczytanie kodu)? — kompromis wygoda vs bezpieczeństwo.
2. Czy backend ma dodatkowo skanować kod po stronie serwera (ta sama lista
   co warstwa 2) i odmawiać zwrotu trafień z listy blokującej?
3. Limit rozmiaru generowanego kodu (obecnie max_tokens 2048 — czy zostaje)?
4. Logowanie incydentów: co zapisujemy, gdy filtr coś zablokuje (bez treści
   promptu użytkownika — patrz temat RODO w notatkach projektu)?
