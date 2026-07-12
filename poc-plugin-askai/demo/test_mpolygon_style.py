# TEST LC: skoro int-index jest ignorowany (jeden bazowy wzór = poziome linie),
# sprawdzamy czy KĄT + KRZYŻ + SKALA dają kontrolę nad wyglądem wypełnienia.
# 3 duże pudła: poziomy / skos 45 / krzyż 45. Jeśli tak -> to jest nasza realna
# paleta hatcha (bez nazwanych wzorów, ale pokrywa 'po skosie'/'krzyżykowo'/gęstość).
# Uwaga: setPatternAngle prawdopodobnie w RADIANACH (0.7854 = 45 stopni). Jak wyjdzie
# prawie poziomo -> API bierze stopnie, powtórzymy z 45.
from pygcad.core import *
from pygcad.pygrx import *

PI4 = 0.78539816339   # 45 stopni w radianach


def styl(ms, x0, W, H, angle, double, opis):
    pline = GcDbPolyline()
    pline.addVertexAt(0, GcGePoint2d(x0, 0), 0, 0, 0)
    pline.addVertexAt(1, GcGePoint2d(x0 + W, 0), 0, 0, 0)
    pline.addVertexAt(2, GcGePoint2d(x0 + W, H), 0, 0, 0)
    pline.addVertexAt(3, GcGePoint2d(x0, H), 0, 0, 0)
    pline.setClosed(True)
    note = opis + "="
    try:
        mpoly = GcDbMPolygon()
        mpoly.appendLoopFromBoundary(pline)
        mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, 1)
        mpoly.setPatternScale(15.0)
        try:
            mpoly.setPatternAngle(angle)
            note += "angleOK "
        except Exception as e:
            note += "angleERR:%s " % type(e).__name__
        if double:
            try:
                mpoly.setPatternDouble(True)
                note += "doubleOK "
            except Exception as e:
                note += "doubleERR:%s " % type(e).__name__
        mpoly.evaluateHatch()
        ms.appendGcDbEntity(mpoly)
        mpoly.close()
    except Exception as e:
        note += "MPOLY_ERR:%s " % type(e).__name__
    ms.appendGcDbEntity(pline)
    pline.close()
    txt = GcDbText(GcGePoint3d(x0 + W / 2.0, H + 300, 0), opis)
    txt.setHeight(350)
    txt.setHorizontalMode(GcDb.TextHorzMode.kTextCenter)
    txt.setAlignmentPoint(GcGePoint3d(x0 + W / 2.0, H + 300, 0))
    ms.appendGcDbEntity(txt)
    txt.close()
    return note


def galeria_styl():
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        bt.close()
        W, H, GAP = 2000, 1500, 800
        wynik = []
        wynik.append(styl(ms, 0 * (W + GAP), W, H, 0.0, False, "poziomy"))
        wynik.append(styl(ms, 1 * (W + GAP), W, H, PI4, False, "skos 45"))
        wynik.append(styl(ms, 2 * (W + GAP), W, H, PI4, True, "krzyz 45"))
        ms.close()
        gcedPrompt("\n[STYL] " + "| ".join(wynik))
    except Exception as err:
        gcedPrompt("\n[STYL BLAD] %s: %s" % (type(err).__name__, str(err)))


galeria_styl()
