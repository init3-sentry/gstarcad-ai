from pygcad.core import *
from pygcad.pygrx import *

def rysuj_tabelke():
    try:
        # Parametry tabelki rysunkowej
        x0, y0 = 0, 0
        width, height = 1800, 600
        row_h = height / 5.0  # 5 pol opisowych ulozonych poziomo

        db = gcdbWorkingDatabase()
        status, blockTable = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        entities = []

        # Ramka zewnetrzna tabelki - prostokat jako polilinia zamknieta
        rama = GcDbPolyline()
        rama.addVertexAt(0, GcGePoint2d(x0, y0), 0, 0, 0)
        rama.addVertexAt(1, GcGePoint2d(x0 + width, y0), 0, 0, 0)
        rama.addVertexAt(2, GcGePoint2d(x0 + width, y0 + height), 0, 0, 0)
        rama.addVertexAt(3, GcGePoint2d(x0, y0 + height), 0, 0, 0)
        rama.setClosed(True)
        entities.append(rama)

        # Poziome linie podzialu pol (5 wierszy)
        for i in range(1, 5):
            y = y0 + i * row_h
            linia = GcDbLine(GcGePoint3d(x0, y, 0), GcGePoint3d(x0 + width, y, 0))
            entities.append(linia)

        # Opisy pol - tekst wysrodkowany w kazdym wierszu
        opisy = ["Projekt", "Rysowal", "Data", "Skala", "Nr rysunku"]
        text_h = row_h * 0.4

        for i, opis in enumerate(opisy):
            # Wiersze liczone od gory tabelki w dol
            y_srodek = y0 + height - (i + 0.5) * row_h
            x_srodek = x0 + width / 2.0

            txt = GcDbText(GcGePoint3d(x_srodek, y_srodek, 0), opis)
            txt.setHeight(text_h)
            txt.setHorizontalMode(GcDb.TextHorzMode.kTextCenter)
            txt.setVerticalMode(GcDb.TextVertMode.kTextVertMid)
            txt.setAlignmentPoint(GcGePoint3d(x_srodek, y_srodek, 0))
            entities.append(txt)

        # Dodanie wszystkich obiektow do przestrzeni modelu
        for ent in entities:
            status, objId = modelSpace.appendGcDbEntity(ent)
            ent.close()

        modelSpace.close()

        gcedPrompt("\nTabelka rysunkowa 1800x600 narysowana w punkcie (0,0).")
    except Exception as err:
        gcedPrompt('\n[BŁĄD]: %s' % err)

rysuj_tabelke()
