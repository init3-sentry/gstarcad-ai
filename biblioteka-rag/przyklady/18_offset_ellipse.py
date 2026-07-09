# Wzorcowa komenda 18 — Kopia elipsy odsunięta o zadany dystans (offset).
#
# Demonstruje operację "offset" (odsunięcie równoległe) na krzywej — tworzy
# nową krzywą odsuniętą o zadaną odległość od oryginału. Pokazuje też rzutowanie
# obiektu na konkretny typ (GcDbEllipse.cast) po sprawdzeniu isKindOf. Wzorzec z
# oficjalnego samples curve.py (funkcja offsetEllipse).
#
# Sposób użycia: APPLOAD, następnie ODSUN_ELIPSE. Narysuj najpierw elipsę
# (polecenie ELLIPSE), potem uruchom komendę i wskaż elipsę — pojawi się jej
# kopia odsunięta o 10 jednostek.
#
# Konwencje (v2 przewodnika + curve.py):
#   - gcedEntSel zwraca RTNORM; sprawdzić isKindOf(GcDbEllipse.desc()) przed cast
#   - GcDbEllipse.cast(obj) po potwierdzeniu typu
#   - (status, curves) = ellipse.getOffsetCurves(dystans) — zwraca listę krzywych
#   - wynik to GcDbEntity — dodać do model space jak zwykle

from pygcad.core.runtime import *
from pygcad.pygrx import *


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


@command(local_name='ODSUN_ELIPSE')
def offsetEllipse():
    """Wskazuje elipsę i tworzy jej kopię odsuniętą o 10 jednostek."""
    try:
        OFFSET_DIST = 10.0

        en = gds_name()
        pt = GcGePoint3d()
        rc = gcedEntSel("\nWskaż elipsę do odsunięcia: ", en, pt)
        if rc != RTNORM:
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        entId = GcDbObjectId()
        gcdbGetObjectId(entId, en)

        status, obj = gcdbOpenObject(entId, GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć wskazanego obiektu.")
            return

        if not obj.isKindOf(GcDbEllipse.desc()):
            obj.close()
            gcutPrintf("\nWskazany obiekt nie jest elipsą. Narysuj elipsę poleceniem ELLIPSE.")
            return

        ellipse = GcDbEllipse.cast(obj)
        status, curves = ellipse.getOffsetCurves(OFFSET_DIST)
        obj.close()

        if not curves or len(curves) == 0:
            gcutPrintf("\n[BŁĄD] Odsunięcie nie zwróciło żadnej krzywej.")
            return

        # curves[0] to nowa krzywa — rzutuj na encję i dodaj do rysunku
        newEntity = GcDbEntity.cast(curves[0])
        if _addToModelSpace(newEntity):
            gcutPrintf(f"\nUtworzono kopię elipsy odsuniętą o {OFFSET_DIST} jednostek.")
        else:
            gcutPrintf("\n[BŁĄD] Nie można dodać odsuniętej krzywej do rysunku.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy odsuwaniu elipsy: {err}")
