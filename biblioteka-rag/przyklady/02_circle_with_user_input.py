# Wzorcowa komenda 02 — Rysowanie okręgu z interakcją użytkownika.
#
# Demonstruje pobieranie danych od użytkownika w trakcie wykonania komendy:
# zapytanie o promień przy pomocy gcedGetReal, sprawdzenie czy użytkownik
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
#   - gcedGetReal / gcedSSGet / gcedGetPoint zwracają RTNORM przy sukcesie
#     (NIE Gcad.eOk — to inna rodzina statusów, "input result")
#   - operacje na bazie porównujemy z Gcad.eOk

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='RYSUJ_OKRAG_Z_PYTANIEM')
def drawCircleByUserRadius():
    """Pyta użytkownika o promień i rysuje okrąg w środku układu współrzędnych."""
    try:
        # Zapytaj użytkownika o promień okręgu
        status, radius = gcedGetReal("\nPodaj promień okręgu (w jednostkach rysunku): ")

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
