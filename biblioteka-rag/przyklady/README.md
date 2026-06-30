# Wzorcowe komendy GstarCAD-a w Pythonie

Ten folder zawiera pięć wzorcowych komend dla GstarCAD 2026, przygotowanych jako wzór do naśladowania dla zespołu pomocy technicznej TMSys.

## Cel

Każda z pięciu komend pokazuje inny wzorzec pracy z biblioteką pygcad. Razem stanowią one referencyjną podstawę dla każdej kolejnej komendy, którą zespół będzie pisał — od typowego rysowania, przez interakcję z użytkownikiem, po automatyzację raportowania.

Komendy są napisane w pełni samodzielnie przez Dawida Jakubowskiego (z asystą Claude'a) i wcześniej zweryfikowane empirycznie w GstarCAD 2026 — to znaczy, że każda z nich gwarantowanie działa.

## Komendy

| Plik | Komenda | Co robi |
|---|---|---|
| `01_line_drawing.py` | `RYSUJ_LINIE_WZORCOWA` | Najprostsza komenda — rysuje wzorcową linię z (0,0,0) do (100,100,0) |
| `02_circle_with_user_input.py` | `RYSUJ_OKRĄG_Z_PYTANIEM` | Demonstruje interakcję — pyta użytkownika o promień, rysuje okrąg |
| `03_rectangle_with_layer.py` | `RYSUJ_POKOJ` | Praca z warstwami — tworzy warstwę POKOJE i rysuje na niej prostokąt |
| `04_layer_audit_report.py` | `AUDYT_WARSTW` | Audyt — iteruje po warstwach, generuje raport, zapisuje do pliku |
| `05_change_selected_color.py` | `ZMIEN_KOLOR_NA_ZIELONY` | Praca z zaznaczeniem — zmienia kolor obiektów wybranych przez użytkownika |

## Jak ich używać

Krok pierwszy — otwórz GstarCAD 2026.
Krok drugi — wpisz w command line polecenie `APPLOAD`.
Krok trzeci — w oknie dialogowym wybierz plik `.py`, który chcesz wczytać, naciśnij „Załaduj".
Krok czwarty — w command line wpisz nazwę komendy (z tabeli wyżej). Komenda się wykona.

Możesz wczytać wszystkie pięć komend od razu — każda z nich rejestruje się pod swoją własną nazwą i nie powodują konfliktu.

## Co warto z nich nauczyć

Patrząc na wzorce kolejno:

**Pierwsza komenda** uczy minimalnego cyklu: otwarcie bazy → dostęp do model space → utworzenie obiektu → dodanie do bazy → zamknięcie wszystkiego → komunikat. Każda następna komenda zawiera ten sam szkielet, tylko z dodatkowymi elementami.

**Druga komenda** uczy interakcji z użytkownikiem przez `gcedGetReal`. Zwróć uwagę na sprawdzanie statusu (`status != 5100`) — pokazuje jak grzecznie obsłużyć anulowanie operacji przez Escape.

**Trzecia komenda** uczy pracy z tabelą warstw. Wzorzec „sprawdź czy warstwa istnieje, utwórz jeśli nie, użyj" jest jednym z najczęściej powtarzanych w skryptach CAD-owych.

**Czwarta komenda** uczy iteracji po tabelach symboli (tu — warstw, ale ten sam wzorzec stosuje się dla bloków, stylów tekstu, stylów wymiarowania). Plus pokazuje, jak generować i zapisywać raport tekstowy.

**Piąta komenda** uczy pracy z zaznaczeniem użytkownika i z bezpiecznym rzutowaniem obiektów (`isKindOf` + `cast`).

## Konwencje, które warto zachowywać

Te konwencje powtarzają się w każdej z pięciu komend — i mają się powtarzać w każdej kolejnej komendzie pisanej dla projektu:

1. **Każda funkcja jest opakowana w blok `try/except`** — łapie wyjątki i komunikuje błąd przez `gcedPrompt`, zamiast wywalać konsolę Pythona w GstarCAD-zie.
2. **Wszystkie komentarze są po polsku.**
3. **Każdy otwarty obiekt jest zamykany** (.close()) w odpowiedniej kolejności.
4. **Komendy mają polskie nazwy** (przez `local_name='POLSKA_NAZWA'`).
5. **Krótka instrukcja użycia jest w nagłówku pliku** — komentarz na samej górze pliku.
6. **Importy są na początku, bez gwiazdek tam gdzie się da uniknąć** (ale wildcard z `pygcad.core` jest tu OK, bo cała ta biblioteka jest mała i przewidywalna).

## Co jeszcze warto pokazać

Te pięć wzorców pokrywa najpopularniejsze potrzeby. Z czasem warto rozszerzyć kolekcję o:

- komendę pracującą z polilinią złożoną (`GcDbPolyline` 2D)
- komendę z wymiarowaniem
- komendę z tekstem wielowierszowym (`GcDbMText`)
- komendę z blokiem (wstawianie z biblioteki bloków)
- komendę przycinającą obiekty (operacja boolowska)

Te rozszerzenia trafią do folderu `przyklady/` w miarę powstawania (w etapie trzecim projektu — galeria mistrzowska).

---

*Wersja: 1.0 — 30 czerwca 2026*
