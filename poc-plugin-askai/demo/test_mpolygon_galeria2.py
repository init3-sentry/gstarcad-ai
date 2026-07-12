# TEST LC: galeria v2 — DUŻE pudła, żeby wzór był czytelny (v1 miał 12 małych = blur).
# 4 prostokąty 2000x1500, indeksy 0/4/8/11, żeby zobaczyć czy int ZMIENIA wzór.
# Jeśli wszystkie 4 wyglądają tak samo -> int ignorowany (jeden wzór).
# Jeśli różne -> int wybiera wzór, zmapujemy pełny zakres osobno.
from pygcad.core import *
from pygcad.pygrx import *


def galeria2():
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        bt.close()

        W, H, GAP = 2000, 1500, 800
        indeksy = [0, 4, 8, 11]
        wynik = []
        for k, idx in enumerate(indeksy):
            x0 = k * (W + GAP)

            pline = GcDbPolyline()
            pline.addVertexAt(0, GcGePoint2d(x0, 0), 0, 0, 0)
            pline.addVertexAt(1, GcGePoint2d(x0 + W, 0), 0, 0, 0)
            pline.addVertexAt(2, GcGePoint2d(x0 + W, H), 0, 0, 0)
            pline.addVertexAt(3, GcGePoint2d(x0, H), 0, 0, 0)
            pline.setClosed(True)

            try:
                mpoly = GcDbMPolygon()
                mpoly.appendLoopFromBoundary(pline)
                st = mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, idx)
                mpoly.setPatternScale(15.0)          # większa skala -> linie rozstawione, czytelne na dużym pudle
                mpoly.evaluateHatch()
                ms.appendGcDbEntity(mpoly)
                mpoly.close()
                wynik.append("%d=%s" % (idx, str(st)))
            except Exception as e:
                wynik.append("%d=ERR:%s" % (idx, type(e).__name__))

            ms.appendGcDbEntity(pline)
            pline.close()

            txt = GcDbText(GcGePoint3d(x0 + W / 2.0, H + 300, 0), "index %d" % idx)
            txt.setHeight(400)
            txt.setHorizontalMode(GcDb.TextHorzMode.kTextCenter)
            txt.setAlignmentPoint(GcGePoint3d(x0 + W / 2.0, H + 300, 0))
            ms.appendGcDbEntity(txt)
            txt.close()

        ms.close()
        gcedPrompt("\n[GALERIA2] " + " | ".join(wynik))
    except Exception as err:
        gcedPrompt("\n[GALERIA2 BLAD] %s: %s" % (type(err).__name__, str(err)))


galeria2()
