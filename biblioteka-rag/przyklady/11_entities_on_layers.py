# Wzorcowa komenda 11 — Rysowanie obiektów na osobnych warstwach z kolorami RGB.
#
# Demonstruje wzorzec „utwórz kilka warstw o różnych kolorach, narysuj obiekty
# i przypisz każdy do właściwej warstwy". Kolor warstwy ustawiany przez
# GcCmColor.setRGB (alternatywa dla setColorIndex — pełny kolor RGB zamiast
# indeksu z palety ACI). Wzorzec kanoniczny z oficjalnego samples
# entity_in_layers.py.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz RYSUJ_SCHEMAT.
# Komenda tworzy dwie warstwy (KONSTRUKCJA czerwona, INSTALACJE zielona)
# i rysuje na nich przykładowy schemat: linię na KONSTRUKCJI, dwa okręgi
# na INSTALACJACH.
#
# Konwencje (v2 przewodnika + entity_in_layers.py):
#   - GcCmColor.setRGB(r, g, b) — kolor pełny; setColorIndex(n) — kolor z palety
#   - entity.setLayer("NAZWA") PO appendGcDbEntity (encja musi być już w bazie)
#   - warstwa tworzona z linetype "CONTINUOUS" jako fallback

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _ensureLayerRGB(database, name, r, g, b):
    """Tworzy warstwę o kolorze RGB, jeśli nie istnieje. Zwraca True przy sukcesie."""
    status, layerTable = database.getLayerTable(GcDb.kForWrite)
    if status != Gcad.eOk:
        gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli warstw.")
        return False
    if layerTable.has(name):
        layerTable.close()
        return True
    record = GcDbLayerTableRecord()
    record.setName(name)
    record.setIsLocked(0)
    color = GcCmColor()
    color.setRGB(r, g, b)
    record.setColor(color)
    layerTable.add(record)
    record.close()
    layerTable.close()
    gcutPrintf(f"\nUtworzono warstwę: {name}")
    return True


def _drawOnLayer(database, entity, layerName):
    """Dodaje encję do model space i przypisuje ją do warstwy."""
    status, blockTable = database.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return False
    status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    blockTable.close()
    if status != Gcad.eOk:
        return False
    modelSpace.appendGcDbEntity(entity)
    entity.setLayer(layerName)
    modelSpace.close()
    entity.close()
    return True


@command(local_name='RYSUJ_SCHEMAT')
def drawSchemaOnLayers():
    """Tworzy dwie warstwy z kolorami RGB i rysuje na nich przykładowy schemat."""
    try:
        database = gcdbWorkingDatabase()

        if not _ensureLayerRGB(database, "KONSTRUKCJA", 255, 0, 0):
            return
        if not _ensureLayerRGB(database, "INSTALACJE", 0, 255, 0):
            return

        # Linia na warstwie KONSTRUKCJA
        line = GcDbLine(GcGePoint3d(0.0, 0.0, 0.0), GcGePoint3d(1000.0, 0.0, 0.0))
        _drawOnLayer(database, line, "KONSTRUKCJA")

        # Dwa okręgi na warstwie INSTALACJE
        normal = GcGeVector3d(0.0, 0.0, 1.0)
        circle1 = GcDbCircle(GcGePoint3d(300.0, 0.0, 0.0), normal, 120.0)
        _drawOnLayer(database, circle1, "INSTALACJE")
        circle2 = GcDbCircle(GcGePoint3d(700.0, 0.0, 0.0), normal, 120.0)
        _drawOnLayer(database, circle2, "INSTALACJE")

        gcutPrintf("\nSchemat narysowany: linia na KONSTRUKCJI, 2 okręgi na INSTALACJACH.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy rysowaniu schematu: {err}")
