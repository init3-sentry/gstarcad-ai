# Wzorcowa komenda 03 — Prostokąt na konkretnej warstwie z auto-utworzeniem warstwy.
#
# Demonstruje pracę z tabelą warstw: sprawdzenie czy warstwa istnieje,
# utworzenie nowej warstwy z konkretnym kolorem (kanoniczny pattern GcCmColor
# + setColor, per oficjalny tablerec.py), rysowanie zamkniętego prostokąta
# 2D poleceniem GcDbPolyline (per oficjalny ployline_dim.py).
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz RYSUJ_POKOJ.
# Komenda utworzy warstwę POKOJE z czerwonym kolorem (jeśli nie istnieje)
# i narysuje na niej prostokąt o wymiarach 5 na 3 metry.
#
# Historia wzorca: pierwsza wersja (2026-06-30) używała newLayer.setColorIndex(1)
# — ta metoda NIE ISTNIEJE na LayerTableRecord (empiryczny AttributeError,
# 2026-07-01, GstarCAD 2027 Plus PL). Poprawka: kolor ustawiamy przez obiekt
# GcCmColor.setColorIndex(1), potem record.setColor(color).
# Ta sama sesja: GcDb3dPolyline + setClosed + appendGcDbEntity CRASHOWAŁO
# GstarCAD-a do desktopu (report do GstarSoft R&D). Zastąpione bezpiecznym
# GcDbPolyline (2D) z addVertexAt.
#
# Konwencje (v2 przewodnika-systemowego):
#   - Layer color: GcCmColor + setColorIndex(idx) na obiekcie koloru, potem
#     record.setColor(color). NIE record.setColorIndex(idx) — nie istnieje.
#   - 2D polyline zamknięta: GcDbPolyline + addVertexAt(index, GcGePoint2d,...)
#     w każdym wierzchołku, zamknięcie przez powrót do startu.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _ensureLayer(database, layerName, colorIndex):
    """Tworzy warstwę o podanej nazwie i kolorze, jeśli nie istnieje.
    Zwraca True w razie sukcesu (lub jeśli warstwa już była)."""
    status, layerTable = database.getLayerTable(GcDb.kForWrite)
    if status != Gcad.eOk:
        gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli warstw.")
        return False

    if layerTable.has(layerName):
        layerTable.close()
        return True

    record = GcDbLayerTableRecord()
    record.setName(layerName)

    # Kanoniczny pattern koloru warstwy (per tablerec.py):
    # kolor ustawiamy na obiekcie GcCmColor, potem GcCmColor przypisujemy do warstwy.
    color = GcCmColor()
    color.setColorIndex(colorIndex)
    record.setColor(color)

    layerTable.add(record)
    record.close()
    layerTable.close()
    gcutPrintf(f"\nUtworzono nową warstwę: {layerName}")
    return True


@command(local_name='RYSUJ_POKOJ')
def drawRoomRectangle():
    """Tworzy warstwę POKOJE (jeśli trzeba) i rysuje na niej prostokąt 5x3."""
    try:
        # Parametry: pokój 5x3 metry, warstwa POKOJE, kolor 1 = czerwony (indeks ACI)
        width = 5.0
        height = 3.0
        layerName = "POKOJE"
        layerColorIndex = 1

        database = gcdbWorkingDatabase()

        # KROK 1: utwórz warstwę POKOJE, jeśli nie istnieje
        if not _ensureLayer(database, layerName, layerColorIndex):
            return

        # KROK 2: otwarcie przestrzeni modelu
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return

        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        # KROK 3: prostokąt jako 2D polyline zamknięta (per ployline_dim.py).
        # UWAGA: NIE używamy GcDb3dPolyline — na GstarCAD 2027 Plus PL
        # kombinacja GcDb3dPolyline + setClosed + appendGcDbEntity crashuje
        # program do desktopu (potwierdzone 2026-07-01).
        pline = GcDbPolyline()
        pline.addVertexAt(0, GcGePoint2d(0.0, 0.0), 0, 0, 0)
        pline.addVertexAt(1, GcGePoint2d(width, 0.0), 0, 0, 0)
        pline.addVertexAt(2, GcGePoint2d(width, height), 0, 0, 0)
        pline.addVertexAt(3, GcGePoint2d(0.0, height), 0, 0, 0)
        # Zamknięcie prostokąta: powrót do punktu startowego (bezpieczniej niż setClosed).
        pline.addVertexAt(pline.numVerts(), GcGePoint2d(0.0, 0.0), 0, 0, 0)

        # Przypisz prostokąt do warstwy POKOJE PRZED dodaniem do rysunku
        pline.setLayer(layerName)

        # KROK 4: dodanie prostokąta do rysunku
        status, plineId = modelSpace.appendGcDbEntity(pline)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można dodać prostokąta do przestrzeni modelu.")

        modelSpace.close()
        pline.close()

        gcutPrintf(f"\nProstokąt {width}x{height} narysowany na warstwie {layerName}.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy rysowaniu pokoju: {err}")
