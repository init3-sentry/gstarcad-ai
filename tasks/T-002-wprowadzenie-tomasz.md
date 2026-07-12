# T-002 — Wprowadzenie do projektu: Tomasz Gach plus weryfikacja wzorcowych komend

| Pole | Wartość |
|---|---|
| Identyfikator | T-002 |
| Etap | pierwszy |
| Przypisany do | **Tomasz Gach** (tomasz.gach [małpa] tmsys.pl) |
| Przewidywany czas | 8 godzin (cztery dni roboczy po dwie godziny) |
| Status | oczekuje |
| Data wejścia | 2026-06-30 |
| Data deklarowanego ukończenia | 2026-07-14 |
| Zależy od | T-004 (zatwierdzenie pakietu) |

## Cel

Przyswojenie pełnego pakietu wprowadzającego (analogicznie do T-001 dla Jakuba) plus dodatkowe zadanie weryfikacyjne dla pięciu wzorcowych komend, które przygotowuje zespół projektowy. Weryfikacja polega na załadowaniu każdej z pięciu komend do GstarCAD 2026 na maszynie Tomasza i sprawdzeniu, czy działa zgodnie z opisem.

## Kryteria akceptacji

- [ ] Wszystkie kryteria z T-001 (lekcje, konto, test) — analogicznie
- [ ] Pięć wzorcowych komend z folderu `biblioteka-rag/przyklady/` załadowanych do GstarCAD 2026 i przetestowanych
- [ ] Dla każdej komendy zapisana krótka notatka (do połowy strony) — czy działa, czy są błędy, jakie uwagi do dokumentacji
- [ ] Pięć notatek wgranych jako pojedynczy plik tekstowy do folderu `przeglady/2026-07-11-weryfikacja-komend-tomasz.md` w repozytorium

## Wskazówki

Tomasz jest doświadczonym specjalistą wsparcia GstarCAD-a, ale weryfikuje tu konkretny aspekt techniczny — czy komenda napisana w nowym, eksperymentalnym pygcad faktycznie się ładuje, kompiluje i działa w aktualnej wersji GstarCAD 2026. Każda komenda powinna być wczytana świeżą instancją GstarCAD-a, na pustym rysunku, bez wcześniej załadowanych innych skryptów.

Weryfikacja jest krytyczna dla całego projektu, bo z tych pięciu wzorcowych komend chłopcy uczą się wzorca pisania własnych. Jeśli któraś nie działa — naprawiamy zanim ruszymy dalej.

## Materiały odniesienia

- Wszystkie lekcje z folderu `dla-pomocy-technicznej/` (jak w T-001)
- Pięć plików `.py` z folderu `biblioteka-rag/przyklady/`
- [`poc-plugin-askai/backend/system-prompt.md`](../poc-plugin-askai/backend/system-prompt.md) jako referencja, gdyby coś było niejasne w kodzie
