# Wzorcowa komenda 02 — Rysowanie okręgu z interakcją użytkownika.
#
# Demonstruje pobieranie danych od użytkownika w trakcie wykonania komendy:
# zapytanie o promień przy pomocy gcedGetReal, sprawdzenie czy użytkownik
# nie anulował operacji, użycie wartości w konstrukcji okręgu.
#
# Sposób użycia: APPLOAD w GstarCAD 2026, następnie wpisz RYSUJ_OKRĄG_Z_PYTANIEM
# w command line. GstarCAD zapyta Cię o promień, podaj go (na przykład 25)
# i naciśnij Enter — okrąg pojawi się w środku rysunku.

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='RYSUJ_OKRĄG_Z_PYTANIEM')
def drawCircleByUserRadius():
    """Pyta użytkownika o promień i rysuje okrąg w środku układu współrzędnych."""
    try:
        # Zapytaj użytkownika o promień okręgu
        status, radius = gcedGetReal("Podaj promień okręgu (w jednostkach rysunku): ")

        # Status 5100 oznacza poprawne pobranie wartości
        # Jeśli użytkownik anulował operację (Escape), wyjdź bez błędu
        if status != 5100:
            gcedPrompt("Anulowano przez użytkownika.")
            return

        # Sprawdź czy podany promień jest sensowny
        if radius <= 0:
            gcedPrompt("Promień musi być liczbą dodatnią. Operacja anulowana.")
            return

        # Pobierz bazę danych rysunku
        database = gcdbWorkingDatabase()

        # Otwórz tabelę bloków i model space
        status, blockTable = database.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        # Przygotuj parametry okręgu — środek, wektor normalny (w GstarCAD-zie zawsze Z = 1
        # dla okręgów leżących płasko na rysunku), promień
        center = GcGePoint3d(0.0, 0.0, 0.0)
        normalVector = GcGeVector3d(0.0, 0.0, 1.0)

        # Utwórz okrąg
        circle = GcDbCircle(center, normalVector, radius)

        # Dodaj okrąg do rysunku
        status, circleId = modelSpace.appendGcDbEntity(circle)

        # Zwolnij obiekty
        modelSpace.close()
        circle.close()

        # Komunikat sukcesu
        gcedPrompt(f"Okrąg o promieniu {radius} narysowany w środku układu.")

    except Exception as err:
        gcedPrompt(f"---- [BŁĄD] przy rysowaniu okręgu: {err}")
