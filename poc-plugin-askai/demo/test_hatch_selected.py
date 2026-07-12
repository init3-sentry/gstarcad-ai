# TEST LC: zakreskuj ZAZNACZONY przez usera obiekt (praca na niepustym rysunku).
# Klucz do rozstrzygnięcia: czy GcDbMPolygon.appendLoopFromBoundary przyjmuje
# encję JUŻ ZAPISANĄ W BAZIE (w dotychczasowych testach polilinia nie była db-resident).
#
# Użycie: 1) narysuj zamkniętą polilinię (PLINE, dowolny nietypowy kształt),
#         2) APPLOAD tego pliku, 3) wpisz komendę ZAKRESKUJ, 4) wskaż polilinię.
# Idiom selekcji skopiowany ze sprawdzonego 18_offset_ellipse / wzorca 13.
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import math


def _addToModelSpace(entity):
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return False
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if status != Gcad.eOk:
        return False
    ms.appendGcDbEntity(entity)
    ms.close()
    entity.close()
    return True


@command(local_name='ZAKRESKUJ')
def zakreskuj():
    """Wskaż zamkniętą polilinię — zostanie zakreskowana skosem 45."""
    try:
        en = gds_name()
        pt = GcGePoint3d()
        rc = gcedEntSel("\nWskaz zamknieta polilinie do zakreskowania: ", en, pt)
        if rc != RTNORM:
            gcutPrintf("\nNic nie wybrano. Anulowano.")
            return

        entId = GcDbObjectId()
        gcdbGetObjectId(entId, en)
        status, obj = gcdbOpenObject(entId, GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc wskazanego obiektu.")
            return

        # Akceptuj lekką GcDbPolyline i ciężką GcDb2dPolyline (zależy od PLINETYPE)
        if obj.isKindOf(GcDbPolyline.desc()):
            boundary = GcDbPolyline.cast(obj)
            typ = "GcDbPolyline"
        elif obj.isKindOf(GcDb2dPolyline.desc()):
            boundary = GcDb2dPolyline.cast(obj)
            typ = "GcDb2dPolyline"
        else:
            klasa = obj.isA().name()
            obj.close()
            gcutPrintf("\nWskazany obiekt to nie polilinia (%s). Narysuj zamknieta polilinie (PLINE)." % klasa)
            return

        mpoly = GcDbMPolygon()
        st_loop = mpoly.appendLoopFromBoundary(boundary)   # <-- KLUCZ: granica z db-resident encji
        obj.close()

        mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, 1)
        mpoly.setPatternScale(10.0)                         # jak za gesto/rzadko -> zmienimy
        mpoly.setPatternAngle(math.pi / 4.0)               # skos 45
        mpoly.evaluateHatch()

        if _addToModelSpace(mpoly):
            gcutPrintf("\n[ZAKRESKUJ] Gotowe. typ=%s appendLoopFromBoundary=%s. Czy ksztalt zakreskowany skosem?"
                       % (typ, str(st_loop)))
        else:
            gcutPrintf("\n[BLAD] Nie mozna dodac hatcha do rysunku.")

    except Exception as err:
        gcutPrintf("\n[ZAKRESKUJ BLAD] %s: %s" % (type(err).__name__, str(err)))
