# Wzorcowa komenda 02 — Rysowanie okręgu z interakcją użytkownika.
#
# Demonstruje pobieranie danych od użytkownika w trakcie wykonania komendy:
# zapytanie o promień przez gcedGetString + parsowanie (gcedGetReal nie działa
# z Pythona — BUG-06), sprawdzenie czy użytkownik
# nie anulował operacji, użycie wartości w konstrukcji okręgu.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz
# RYSUJ_OKRAG_Z_PYTANIEM w command line. GstarCAD zapyta o promień —
# podaj go (np. 25), Enter — okrąg pojawi się w środku układu.
#
# Uwaga o nazwie komendy: świadomie bez polskiego "Ą" — command line
# GstarCAD-a nie renderuje pewnych diakrytyków w niektórych wersjach,
# więc zbieramy nazwy komend do ASCII.
#
# Konwencje (v2 przewodnika-systemowego):
#   - gcedSSGet / gcedGetPoint / gcedGetString zwracają RTNORM przy sukcesie
#   - gcedGetReal JEST NIEUŻYWALNY z Pythona (parametr wyjściowy) — pytaj
#     tekstem przez gcedGetString i parsuj sam. Patrz BUG-06 w ledgerze.
#     (NIE Gcad.eOk — to inna rodzina statusów, "input result")
#   - operacje na bazie porównujemy z Gcad.eOk

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='RYSUJ_OKRAG_Z_PYTANIEM')
def drawCircleByUserRadius():
    """Pyta użytkownika o promień i rysuje okrąg w środku układu współrzędnych."""
    try:
        # Zapytaj użytkownika o promień okręgu
        # ⚠️ NIE UŻYWAJ gcedGetReal — pygcad wystawia go jako
        #      (prompt: str, result: float) -> int
        #    czyli z parametrem WYJŚCIOWYM, którego z Pythona nie da się wypełnić
        #    (float jest niezmienny). Wywala się z TypeError. Potwierdzone empirycznie
        #    2026-07-16 (Issue #32) — ten wzorzec uczył wcześniej BŁĘDNEJ formy
        #      status, radius = gcedGetReal(prompt)
        #    i model ją skopiował do narzędzia, które poszło do testów.
        #    Poprawnie: pytamy tekstem i parsujemy sami.
        status, tekst = gcedGetString(1, "\nPodaj promień okręgu (w jednostkach rysunku): ")
        radius = 0.0
        if status == RTNORM and tekst and tekst.strip():
            try:
                radius = float(tekst.strip().replace(",", "."))   # przecinek dziesiętny PL
            except ValueError:
                gcutPrintf("\n'%s' to nie jest liczba. Operacja anulowana." % tekst)
                return

        # RTNORM = użytkownik podał wartość poprawnie. Cokolwiek innego
        # (Escape, puste wejście, błąd parsowania) — anulujemy komendę.
        if status != RTNORM:
            gcutPrintf("\nAnulowano przez użytkownika.")
            return

        # Sprawdź czy podany promień jest sensowny
        if radius <= 0:
            gcutPrintf("\nPromień musi być liczbą dodatnią. Operacja anulowana.")
            return

        # Pobierz bazę danych rysunku
        database = gcdbWorkingDatabase()

        # Otwórz tabelę bloków i model space
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return

        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        # Przygotuj parametry okręgu: środek, wektor normalny (Z=1 dla okręgu
        # leżącego płasko na płaszczyźnie XY), promień
        center = GcGePoint3d(0.0, 0.0, 0.0)
        normalVector = GcGeVector3d(0.0, 0.0, 1.0)

        # Utwórz okrąg
        circle = GcDbCircle(center, normalVector, radius)

        # Dodaj okrąg do rysunku
        status, circleId = modelSpace.appendGcDbEntity(circle)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można dodać okręgu do przestrzeni modelu.")

        # Zwolnij obiekty
        modelSpace.close()
        circle.close()

        gcutPrintf(f"\nOkrąg o promieniu {radius} narysowany w środku układu.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy rysowaniu okręgu: {err}")
