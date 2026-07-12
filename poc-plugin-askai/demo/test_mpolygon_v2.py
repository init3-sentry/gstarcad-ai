# TEST LC v2: GcDbMPolygon — po tym jak setPattern('ANSI31') padł (stub miał rację:
# patName to int, nie string). v2 sprawdza DWIE rzeczy naraz:
#   (a) czy sam obiekt GcDbMPolygon w ogóle się RYSUJE (append mimo wszystko),
#   (b) czy setPattern z int-em przechodzi.
# Odpalić przez APPLOAD. Szukać: wypełniony/obrysowany prostokąt 400x200 + komunikat [MPOLY2].
from pygcad.core import *
from pygcad.pygrx import *


def test_mpolygon_v2():
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        bt.close()

        pline = GcDbPolyline()
        pline.addVertexAt(0, GcGePoint2d(0, 0), 0, 0, 0)
        pline.addVertexAt(1, GcGePoint2d(400, 0), 0, 0, 0)
        pline.addVertexAt(2, GcGePoint2d(400, 200), 0, 0, 0)
        pline.addVertexAt(3, GcGePoint2d(0, 200), 0, 0, 0)
        pline.setClosed(True)

        mpoly = GcDbMPolygon()
        st_loop = mpoly.appendLoopFromBoundary(pline)

        # setPattern chce patName:int (potwierdzone na LC). Próbujemy int=1, ale NIE
        # przerywamy jeśli padnie — chcemy zobaczyć, czy mpoly sam z siebie się rysuje.
        note = ""
        try:
            st_pat = mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, 1)
            note += "setPattern(int=1)=%s " % str(st_pat)
        except Exception as e1:
            note += "setPattern(int) padl:%s " % type(e1).__name__
        try:
            mpoly.setPatternScale(2.0)
        except Exception:
            pass
        try:
            st_eval = mpoly.evaluateHatch()
            note += "eval=%s " % str(st_eval)
        except Exception as e2:
            note += "eval padl:%s " % type(e2).__name__

        # KLUCZOWE: dołóż mpoly do rysunku niezależnie od patternu
        status, oid_m = ms.appendGcDbEntity(mpoly)
        status, oid_p = ms.appendGcDbEntity(pline)
        mpoly.close()
        pline.close()
        ms.close()

        gcedPrompt("\n[MPOLY2] loop=%s %s-> czy widac wypelniony/obrysowany prostokat 400x200?"
                   % (str(st_loop), note))
    except Exception as err:
        gcedPrompt("\n[MPOLY2 BLAD] %s: %s" % (type(err).__name__, str(err)))


test_mpolygon_v2()
