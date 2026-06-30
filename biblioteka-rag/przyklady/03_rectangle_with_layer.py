# Wzorcowa komenda 03 — Prostokąt na konkretnej warstwie z auto-utworzeniem warstwy.
#
# Demonstruje pracę z tabelą warstw: sprawdzenie czy warstwa istnieje,
# utworzenie nowej warstwy z konkretnym kolorem, rysowanie obiektu na tej
# warstwie. Używa polilinii zamkniętej (GcDb3dPolyline) jako prostokąta.
#
# Sposób użycia: APPLOAD w GstarCAD 2026, następnie wpisz RYSUJ_POKOJ. Komenda
# automatycznie utworzy warstwę POKOJE (jeśli nie istnieje) z czerwonym kolorem
# i narysuje na niej prostokąt o wymiarach 5 na 3 metry.

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='RYSUJ_POKOJ')
def drawRoomRectangle():
    """Tworzy warstwę POKOJE (jeśli trzeba) i rysuje na niej prostokąt 5x3."""
    try:
        # Wymiary prostokąta — domyślnie pokój 5x3 metrów
        width = 5.0
        height = 3.0
        layerName = "POKOJE"

        # Pobierz bazę danych
        database = gcdbWorkingDatabase()

        # KROK 1: utworzenie warstwy POKOJE jeśli nie istnieje
        status, layerTable = database.getLayerTable(GcDb.OpenMode.kForWrite)

        # Sprawdź czy warstwa już istnieje w tabeli warstw
        if not layerTable.has(layerName):
            # Utwórz nowy rekord warstwy
            newLayer = GcDbLayerTableRecord()
            newLayer.setName(layerName)
            # Kolor 1 = czerwony (standard GstarCAD-a/AutoCAD-a)
            newLayer.setColorIndex(1)
            # Dodaj nowy rekord do tabeli warstw
            status, newLayerId = layerTable.add(newLayer)
            newLayer.close()
            gcedPrompt(f"Utworzono nową warstwę: {layerName}")

        # Zamknij tabelę warstw
        layerTable.close()

        # KROK 2: otwarcie przestrzeni modelu
        status, blockTable = database.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        # KROK 3: utworzenie prostokąta jako polilinii zamkniętej
        rectangle = GcDb3dPolyline()

        # Cztery wierzchołki prostokąta, idą zgodnie z ruchem wskazówek zegara
        rectangle.appendVertex(GcDb3dPolylineVertex(GcGePoint3d(0.0, 0.0, 0.0)))
        rectangle.appendVertex(GcDb3dPolylineVertex(GcGePoint3d(width, 0.0, 0.0)))
        rectangle.appendVertex(GcDb3dPolylineVertex(GcGePoint3d(width, height, 0.0)))
        rectangle.appendVertex(GcDb3dPolylineVertex(GcGePoint3d(0.0, height, 0.0)))

        # Zamknij polilinię (połącz ostatni punkt z pierwszym)
        rectangle.setClosed(True)

        # Przypisz prostokąt do warstwy POKOJE
        rectangle.setLayer(layerName)

        # KROK 4: dodanie prostokąta do rysunku
        status, rectangleId = modelSpace.appendGcDbEntity(rectangle)
        modelSpace.close()
        rectangle.close()

        gcedPrompt(f"Prostokąt {width}x{height} narysowany na warstwie {layerName}.")

    except Exception as err:
        gcedPrompt(f"---- [BŁĄD] przy rysowaniu pokoju: {err}")
