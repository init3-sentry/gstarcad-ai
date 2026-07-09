# Wzorcowa komenda 08 — Wstawianie referencji bloku w wybranym punkcie.
#
# Demonstruje pracę z blokami: sprawdzenie czy blok istnieje w tabeli bloków,
# utworzenie prostego bloku "GS_MARKER" (krzyżyk z dwóch linii) jeśli go nie ma,
# wstawienie referencji tego bloku w punkcie wskazanym przez użytkownika.
# Wzorzec pracy z BlockReference bierzemy z oficjalnego samples
# dynBlockTableReference.py.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz WSTAW_MARKER.
# Komenda utworzy blok GS_MARKER (jeśli nie istnieje) i zapyta o punkt
# wstawienia — w tym punkcie pojawi się krzyżyk 20x20 jako referencja bloku.
#
# Konwencje (v2 przewodnika-systemowego + dynBlockTableReference.py):
#   - Definicja bloku = nowy GcDbBlockTableRecord dodany do BlockTable
#   - Encje wewnątrz bloku dodajemy do jego BlockTableRecord (nie do model space!)
#   - Referencja bloku = GcDbBlockReference(punkt_wstawienia_GcGePoint3d, block_id)
#   - block_id pobieramy przez blockTable.getObjIdAt("nazwa_bloku")
#
# UWAGA (empirycznie 2026-07-09, GstarCAD 2027 Plus PL): blockTable.add(record)
# zwraca GOŁY ErrorStatus, NIE tuple (status, id) — jak layerTable.add. Dlatego
# NIE rozpakowujemy add(); id definicji pobieramy osobno przez getObjIdAt PO
# dodaniu rekordu. (Odróżnić od getObjIdAt / appendGcDbEntity, które zwracają tuple.)

from pygcad.core.runtime import *
from pygcad.pygrx import *


BLOCK_NAME = "GS_MARKER"
MARKER_SIZE = 10.0  # połowa długości ramienia krzyżyka


def _ensureMarkerBlock(database):
    """Tworzy blok GS_MARKER (krzyżyk z dwóch linii), jeśli nie istnieje.
    Zwraca ObjectId definicji bloku."""
    status, blockTable = database.getBlockTable(GcDb.kForWrite)
    if status != Gcad.eOk:
        gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
        return None

    if blockTable.has(BLOCK_NAME):
        status, blockId = blockTable.getObjIdAt(BLOCK_NAME)
        blockTable.close()
        return blockId

    # Definicja nowego bloku: nowy BlockTableRecord z dwiema liniami.
    # add() zwraca goły status (NIE tuple) — nie rozpakowujemy.
    blockDef = GcDbBlockTableRecord()
    blockDef.setName(BLOCK_NAME)
    blockTable.add(blockDef)

    # Dwie linie tworzące krzyżyk (poziomą i pionową) — dodajemy je
    # DO REKORDU BLOKU, nie do model space.
    lineH = GcDbLine(
        GcGePoint3d(-MARKER_SIZE, 0.0, 0.0),
        GcGePoint3d(MARKER_SIZE, 0.0, 0.0),
    )
    blockDef.appendGcDbEntity(lineH)
    lineH.close()

    lineV = GcDbLine(
        GcGePoint3d(0.0, -MARKER_SIZE, 0.0),
        GcGePoint3d(0.0, MARKER_SIZE, 0.0),
    )
    blockDef.appendGcDbEntity(lineV)
    lineV.close()
    blockDef.close()

    # Id definicji bloku pobieramy osobno PO dodaniu (add nie zwraca id)
    status, blockId = blockTable.getObjIdAt(BLOCK_NAME)
    blockTable.close()
    if status != Gcad.eOk:
        gcutPrintf("\n[BŁĄD] Nie można odczytać id nowo utworzonego bloku.")
        return None

    gcutPrintf(f"\nUtworzono nowy blok: {BLOCK_NAME}")
    return blockId


@command(local_name='WSTAW_MARKER')
def insertMarkerBlock():
    """Zapewnia istnienie bloku GS_MARKER i wstawia jego referencję w punkcie."""
    try:
        database = gcdbWorkingDatabase()

        # KROK 1: upewnij się, że definicja bloku istnieje
        blockId = _ensureMarkerBlock(database)
        if blockId is None:
            return

        # KROK 2: pobierz punkt wstawienia od użytkownika
        insertPoint = GcGePoint3d()
        status = gcedGetPoint(None, "\nWskaż punkt wstawienia markera: ", insertPoint)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # KROK 3: otwórz model space i wstaw referencję bloku
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return

        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        # Referencja bloku = punkt wstawienia + id definicji bloku
        blockRef = GcDbBlockReference(insertPoint, blockId)

        status, refId = modelSpace.appendGcDbEntity(blockRef)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można dodać referencji bloku.")

        modelSpace.close()
        blockRef.close()

        gcutPrintf(f"\nMarker {BLOCK_NAME} wstawiony w punkcie ({insertPoint.x:.2f}, {insertPoint.y:.2f}).")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy wstawianiu markera: {err}")
