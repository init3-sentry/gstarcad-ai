# Wzorcowa komenda 10 — Eksport migawki rysunku (dwa okręgi wzorcowe) do DWG.
#
# Demonstruje tworzenie nowej pustej bazy danych GcDbDatabase, wypełnianie
# jej encjami w pamięci, i zapis do pliku DWG na Pulpicie użytkownika.
# Wzorzec kanoniczny z oficjalnego samples testdb.py.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz
# ZAPISZ_MIGAWKE_DWG. Komenda utworzy plik "migawka_wzorcowa.dwg" na Pulpicie
# zawierający dwa wzorcowe okręgi (o promieniu 5 w punktach (10,10,0)
# i (30,30,0)).
#
# Uwaga bezpieczeństwa — zgodnie z §Safety v2 przewodnika-systemowego zapis
# do pliku wymaga świadomej intencji użytkownika. Ten wzorzec zawsze pisze
# do tej samej z góry znanej lokalizacji (Pulpit) i pod tą samą z góry znaną
# nazwą — nigdy nie nadpisuje istniejących plików bez ostrzeżenia.
#
# Konwencje (v2 przewodnika-systemowego + testdb.py):
#   - GcDbDatabase(True, False) — nowa pusta baza (parametry: buildDefaultDrawing, noDocument)
#   - Praca z bazą identyczna jak z gcdbWorkingDatabase() (getBlockTable itd.)
#   - database.saveAs(file_path) — status musi być Gcad.eOk

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os


@command(local_name='ZAPISZ_MIGAWKE_DWG')
def saveSnapshotDwg():
    """Tworzy nową bazę z dwoma okręgami wzorcowymi i zapisuje jako DWG na Pulpicie."""
    try:
        desktopPath = os.path.expanduser("~/Desktop")
        filePath = os.path.join(desktopPath, "migawka_wzorcowa.dwg")

        # Ostrzeżenie jeśli plik istnieje — nie chcemy nadpisywać niespodzianek
        if os.path.exists(filePath):
            gcutPrintf(
                f"\nPlik już istnieje ({filePath}). Zostanie nadpisany. "
                "Jeśli chcesz zachować poprzednią wersję — zmień nazwę i uruchom ponownie."
            )

        # KROK 1: utwórz nową, pustą bazę danych (kanonicznie per testdb.py)
        database = GcDbDatabase(True, False)

        # KROK 2: dostęp do model space nowej bazy
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków nowej bazy.")
            return

        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu nowej bazy.")
            return

        # KROK 3: dodaj dwa wzorcowe okręgi
        normalVector = GcGeVector3d(0.0, 0.0, 1.0)

        circle1 = GcDbCircle(GcGePoint3d(10.0, 10.0, 0.0), normalVector, 5.0)
        modelSpace.appendGcDbEntity(circle1)
        circle1.close()

        circle2 = GcDbCircle(GcGePoint3d(30.0, 30.0, 0.0), normalVector, 5.0)
        modelSpace.appendGcDbEntity(circle2)
        circle2.close()

        modelSpace.close()

        # KROK 4: zapis bazy do pliku
        status = database.saveAs(filePath)
        if status != Gcad.eOk:
            gcutPrintf(f"\n[BŁĄD] Zapis pliku DWG nie powiódł się (status: {status}).")
            return

        gcutPrintf(f"\nMigawka DWG zapisana: {filePath}")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy zapisie migawki DWG: {err}")
