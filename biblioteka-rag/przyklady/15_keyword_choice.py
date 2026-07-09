# Wzorcowa komenda 15 — Wybór opcji przez słowo kluczowe (keyword).
#
# Demonstruje pobieranie od użytkownika WYBORU z listy opcji (nie liczby, nie
# punktu) przez gcedInitGet + gcedGetKword. To standardowy sposób, w jaki komendy
# CAD-owe oferują tryby ("Wpisz opcję [Kwadrat/Koło/Trójkąt]"). Wzorzec z
# oficjalnego samples curve.py.
#
# Sposób użycia: APPLOAD, następnie WYBIERZ_KSZTALT. Komenda zapyta o kształt
# (Kwadrat/Kolo/Trojkat), a po wyborze narysuje go w środku układu.
#
# Konwencje (v2 przewodnika + curve.py):
#   - gcedInitGet(0, "Kwadrat Kolo Trojkat") — rejestruje dozwolone słowa
#   - (rc, kw) = gcedGetKword("prompt [Kwadrat/Kolo/Trojkat]: ")
#   - sukces = RTNORM; RTNONE = użytkownik dał Enter (opcja domyślna)
#   - słowa kluczowe bez polskich diakrytyków (Kolo, nie Koło)

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _modelSpace():
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    return ms if status == Gcad.eOk else None


@command(local_name='WYBIERZ_KSZTALT')
def chooseShape():
    """Pyta o kształt przez słowo kluczowe i rysuje wybrany kształt."""
    try:
        # Zarejestruj dozwolone słowa kluczowe, potem zapytaj
        gcedInitGet(0, "Kwadrat Kolo Trojkat")
        rc, kw = gcedGetKword("\nWybierz kształt [Kwadrat/Kolo/<Trojkat>]: ")

        # RTNONE = Enter bez wpisania = opcja domyślna (Trojkat)
        if rc == RTNONE:
            kw = "Trojkat"
        elif rc != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        ms = _modelSpace()
        if ms is None:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        if kw == "Kolo":
            ent = GcDbCircle(GcGePoint3d(0, 0, 0), GcGeVector3d(0, 0, 1), 50.0)
            ms.appendGcDbEntity(ent)
            ent.close()
        elif kw == "Kwadrat":
            pline = GcDbPolyline()
            pline.addVertexAt(0, GcGePoint2d(-50, -50), 0, 0, 0)
            pline.addVertexAt(1, GcGePoint2d(50, -50), 0, 0, 0)
            pline.addVertexAt(2, GcGePoint2d(50, 50), 0, 0, 0)
            pline.addVertexAt(3, GcGePoint2d(-50, 50), 0, 0, 0)
            pline.addVertexAt(pline.numVerts(), GcGePoint2d(-50, -50), 0, 0, 0)
            ms.appendGcDbEntity(pline)
            pline.close()
        else:  # Trojkat
            pline = GcDbPolyline()
            pline.addVertexAt(0, GcGePoint2d(-50, -40), 0, 0, 0)
            pline.addVertexAt(1, GcGePoint2d(50, -40), 0, 0, 0)
            pline.addVertexAt(2, GcGePoint2d(0, 50), 0, 0, 0)
            pline.addVertexAt(pline.numVerts(), GcGePoint2d(-50, -40), 0, 0, 0)
            ms.appendGcDbEntity(pline)
            pline.close()

        ms.close()
        gcutPrintf(f"\nNarysowano kształt: {kw}.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy wyborze kształtu: {err}")
