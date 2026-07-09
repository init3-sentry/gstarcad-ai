# Wzorcowa komenda 01 — Rysowanie linii.
#
# Wzorzec dla zespołu pomocy technicznej projektu gstarcad-ai.
# Demonstruje minimalną komendę GstarCAD-a w Pythonie:
# otwarcie bieżącej bazy danych, dostęp do przestrzeni modelu, utworzenie
# obiektu linii, dodanie go do rysunku, zamknięcie wszystkiego, raport
# do command line.
#
# Sposób użycia: Wczytaj plik w GstarCAD 2026/2027 poleceniem APPLOAD.
# Następnie wpisz w command line nazwę RYSUJ_LINIE_WZORCOWA — komenda
# rysuje linię od punktu (0,0,0) do punktu (100,100,0).
#
# Konwencje (v2 przewodnika-systemowego):
#   - status z operacji na bazie porównujemy z Gcad.eOk (== 0)
#   - stałe trybu otwarcia: GcDb.kForRead / GcDb.kForWrite (jak w oficjalnych samples)
#   - komunikaty przez gcutPrintf z prefixem "\n"

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='RYSUJ_LINIE_WZORCOWA')
def drawSampleLine():
    """Rysuje wzorcową linię od punktu (0,0,0) do (100,100,0)."""
    try:
        # Pobierz uchwyt bieżącej bazy danych rysunku
        database = gcdbWorkingDatabase()

        # Otwórz tabelę bloków do odczytu
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return

        # Otwórz przestrzeń modelu (Model Space) do zapisu
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        # Utwórz dwa punkty 3D dla początku i końca linii
        startPoint = GcGePoint3d(0.0, 0.0, 0.0)
        endPoint = GcGePoint3d(100.0, 100.0, 0.0)

        # Utwórz obiekt linii w pamięci (jeszcze nie dodany do rysunku)
        line = GcDbLine(startPoint, endPoint)

        # Dodaj linię do przestrzeni modelu (do bazy danych rysunku)
        status, lineId = modelSpace.appendGcDbEntity(line)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można dodać linii do przestrzeni modelu.")

        # Zwolnij obiekt linii i przestrzeni modelu (odwrotna kolejność do otwarcia)
        modelSpace.close()
        line.close()

        gcutPrintf("\nWzorcowa linia narysowana pomyślnie.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy rysowaniu linii: {err}")
