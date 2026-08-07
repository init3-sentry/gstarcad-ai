# Wzorcowa komenda 24 — Zakreskowanie WSKAZANEGO obiektu (hatch na istniejącej geometrii).
#
# Realny scenariusz pracy na NIEPUSTYM rysunku: użytkownik ma narysowaną zamkniętą
# polilinię (dowolny kształt) i chce ją wypełnić kreskowaniem. Komenda prosi o
# wskazanie obiektu i kreskuje go skosem 45°.
#
# Zwalidowane na LC 2026-07-12 (GstarCAD 2027 Premium) na CELOWO nietypowym,
# SAMOPRZECINAJĄCYM SIĘ kształcie: `appendLoopFromBoundary` = eOk na encji JUŻ
# ZAPISANEJ w bazie (nie tylko na świeżej), wypełnił całość poprawnie.
#
# Sposób użycia: narysuj zamkniętą polilinię (PLINE, zamknij ją), APPLOAD tego pliku,
# wpisz komendę ZAKRESKUJ, wskaż polilinię.
#
# Konwencje / uwagi:
#   - Wypełnienie przez GcDbMPolygon (GcDbHatch NIE ma appendLoop — patrz przewodnik).
#   - Granica to POJEDYNCZA krzywa: Circle / GcDbPolyline / GcDb2dPolyline. Zbiór
#     luźnych linii+łuków albo elipsa/splajn wymagałyby wykrywania obrysu (BPOLY-style).
#   - Paleta wyglądu: setPatternAngle (RADIANY: 0=poziomo, pi/4=45°), setPatternDouble
#     (krzyż), setPatternScale (gęstość). Nazwanych wzorów ANSI nie ma (index ignorowany).
#   - Idiom selekcji jak wzorzec 13 / 18_offset: gds_name + gcedEntSel +
#     gcdbGetObjectId + gcdbOpenObject + isKindOf + cast.

# UWAGA: to WZORZEC DYDAKTYCZNY (demo API kreskowania GcDbMPolygon), NIE narzędzie klienckie.
# Kompletne kreskowanie (skos/kratka/kąt/odstępy) daje natywny HATCH GstarCAD — nie dublujemy
# (REGUŁA #0). Dlatego BEZ bloku @KATALOG — nie wchodzi do katalogu klienckiego. Wartość AI
# dla hatchu = język naturalny przez ASKAI ("wypełnij w kratkę co 5mm"), nie hardcodowany skrypt.

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
            boundary = obj   # typ potwierdzony isKindOf; gcdbOpenObject zwraca typowany obiekt — bez .cast() (BUG-07)
            typ = "GcDbPolyline"
        elif obj.isKindOf(GcDb2dPolyline.desc()):
            boundary = obj   # typ potwierdzony isKindOf; gcdbOpenObject zwraca typowany obiekt — bez .cast() (BUG-07)
            typ = "GcDb2dPolyline"
        else:
            klasa = obj.isA().name()
            obj.close()
            gcutPrintf("\nWskazany obiekt to nie polilinia (%s). Narysuj zamknieta polilinie (PLINE)." % klasa)
            return

        mpoly = GcDbMPolygon()
        st_loop = mpoly.appendLoopFromBoundary(boundary)   # granica z db-resident encji (zaznaczonej)
        obj.close()

        mpoly.setPattern(GcDbHatch.HatchPatternType.kPreDefined, 1)   # index ignorowany, dawaj 1
        mpoly.setPatternScale(10.0)                                   # gęstość — dobierz do rozmiaru
        mpoly.setPatternAngle(math.pi / 4.0)                          # skos 45 (radiany); 0=poziomo
        # mpoly.setPatternDouble(True)                                # odkomentuj = krzyżykowo
        mpoly.evaluateHatch()

        if _addToModelSpace(mpoly):
            gcutPrintf("\n[ZAKRESKUJ] Gotowe. typ=%s appendLoopFromBoundary=%s." % (typ, str(st_loop)))
        else:
            gcutPrintf("\n[BLAD] Nie mozna dodac hatcha do rysunku.")

    except Exception as err:
        gcutPrintf("\n[ZAKRESKUJ BLAD] %s: %s" % (type(err).__name__, str(err)))
