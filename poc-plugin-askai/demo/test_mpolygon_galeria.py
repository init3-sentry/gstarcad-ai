# TEST LC: galeria wzorów GcDbMPolygon — mapowanie index -> wzór.
# setPattern(kPreDefined, patName:int) chce INT; nie znamy który int = który wzór.
# Rysuje rząd prostokątów 0..11, każdy z setPattern(..., i) + numer nad nim.
# Jeden APPLOAD -> jeden screen -> mapujemy który numer daje który wzór
# (i dopasowujemy do nazwanych wzorów GstarCAD: ANSI31=45° linie, ANSI37=krzyż, itd.).
# Kolejność wywołań jak w działającym test_mpolygon_v2 (appendLoopFromBoundary PRZED append pline).
from pygcad.core import *
from pygcad.pygrx import *


def galeria_wzorcow():
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        bt.close()

        W, H, GAP = 400, 300, 150
        wynik = []
        for i in range(0, 12):                      # indeksy wzoru 0..11
            x0 = i * (W + GAP)

            pline = GcDbPolyline()                   # granica (jeszcze NIE w bazie)
            pline.addVertexAt(0, GcGePoint2d(x0, 0), 0, 0, 0)
            pline.addVertexAt(1, GcGePoint2d(x0 + W, 0), 0, 0, 0)
            pline.addVertexAt(2, GcGePoint2d(x0 + W, H), 0, 0, 0)
            pline.addVertexAt(3, GcGePoint2d(x0, H), 0, 0, 0)
            pline.setClosed(True)

            try:
                mpoly = GcDbMPolygon()
                mpoly.appendLoopFromBoundary(pline)  # PRZED append pline (jak w v2)
                st = mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, i)
                mpoly.setPatternScale(3.0)
                mpoly.evaluateHatch()
                ms.appendGcDbEntity(mpoly)
                mpoly.close()
                wynik.append("%d=%s" % (i, str(st)))
            except Exception as e:
                wynik.append("%d=ERR:%s" % (i, type(e).__name__))

            ms.appendGcDbEntity(pline)               # dorysuj obrys
            pline.close()

            txt = GcDbText(GcGePoint3d(x0 + W / 2.0, H + 60, 0), str(i))   # numer nad prostokątem
            txt.setHeight(120)
            txt.setHorizontalMode(GcDb.TextHorzMode.kTextCenter)
            txt.setAlignmentPoint(GcGePoint3d(x0 + W / 2.0, H + 60, 0))
            ms.appendGcDbEntity(txt)
            txt.close()

        ms.close()
        gcedPrompt("\n[GALERIA] " + " | ".join(wynik))
    except Exception as err:
        gcedPrompt("\n[GALERIA BLAD] %s: %s" % (type(err).__name__, str(err)))


galeria_wzorcow()
