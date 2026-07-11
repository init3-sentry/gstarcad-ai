# TEST LC: programowe wypełnienie przez GcDbMPolygon (droga OMIJAJĄCA GcDbHatch).
# Cel: rozstrzygnąć czy pygcad potrafi zrobić kreskowanie kodem — GcDbHatch nie ma
# metody dodania granicy, ale GcDbMPolygon ma appendLoopFromBoundary + evaluateHatch.
# Odpalić przez APPLOAD (rysuje od razu, bez @command). Szukać: zakreskowany prostokąt
# ANSI31 400x200 w (0,0) + komunikat ze statusami w konsoli.
#
# Uwaga do sprawdzenia: stub typuje setPattern(patType, patName: int), ale nazwa wzoru
# to string "ANSI31". Jeśli poleci TypeError na setPattern — to jest ta rozbieżność.
from pygcad.core import *
from pygcad.pygrx import *


def test_mpolygon():
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        bt.close()

        # Granica: zamknięty prostokąt 400x200 jako lekka polilinia
        pline = GcDbPolyline()
        pline.addVertexAt(0, GcGePoint2d(0, 0), 0, 0, 0)
        pline.addVertexAt(1, GcGePoint2d(400, 0), 0, 0, 0)
        pline.addVertexAt(2, GcGePoint2d(400, 200), 0, 0, 0)
        pline.addVertexAt(3, GcGePoint2d(0, 200), 0, 0, 0)
        pline.setClosed(True)

        # MPolygon z wypełnieniem zbudowanym z tej granicy
        mpoly = GcDbMPolygon()
        st_loop = mpoly.appendLoopFromBoundary(pline)

        # Enum wzoru: GcDbHatch.HatchPatternType (NIE GcDb, NIE GcDbMPolygon) — sprawdzone w stubach
        st_pat = mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, "ANSI31")
        mpoly.setPatternScale(10.0)      # skala 10 -> linie widoczne na 400x200 (nie czarna plama)
        st_eval = mpoly.evaluateHatch()

        status, oid_m = ms.appendGcDbEntity(mpoly)
        status, oid_p = ms.appendGcDbEntity(pline)   # dorysuj też sam obrys dla porównania
        mpoly.close()
        pline.close()
        ms.close()

        gcedPrompt("\n[MPOLY] appendLoop=%s setPattern=%s eval=%s — sprawdz czy prostokat jest ZAKRESKOWANY ANSI31"
                   % (str(st_loop), str(st_pat), str(st_eval)))
    except Exception as err:
        gcedPrompt("\n[MPOLY BLAD] %s: %s" % (type(err).__name__, str(err)))


test_mpolygon()
