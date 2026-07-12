# Generator sceny testowej dla wzorca 26 (AUDYTZ).
# Rysuje obiekty CELOWO na różnych wysokościach Z, żeby audyt miał co wykryć:
#   - 3 linie na Z=0      (płaskie, poprawne)
#   - 2 linie na Z=10     (uciekłe w Z)
#   - 1 okrąg na Z=25     (uciekły w Z)
# Oczekiwany wynik AUDYTZ: 3 obiekty poza Z=0 (2 linie + 1 okrąg).
#
# Użycie: APPLOAD tego pliku → komenda SCENA_Z → potem APPLOAD 26_audit_z_axis.py →
# komenda AUDYTZ → w command line ma być „OBIEKTY POZA Z=0: 3" i podswietlone 3 obiekty.
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *


def _ms():
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    return ms if status == Gcad.eOk else None


@command(local_name='SCENA_Z')
def scena_z():
    """Rysuje scenę testową: 3 obiekty płaskie (Z=0) + 3 uciekłe w Z."""
    try:
        ms = _ms()
        if ms is None:
            gcutPrintf("\n[SCENA_Z BLAD] Nie mozna otworzyc modelu.")
            return

        # 3 linie na Z=0 (poprawne)
        for i in range(3):
            y = i * 10.0
            ln = GcDbLine(GcGePoint3d(0, y, 0), GcGePoint3d(50, y, 0))
            ms.appendGcDbEntity(ln)
            ln.close()

        # 2 linie na Z=10 (uciekłe)
        for i in range(2):
            y = i * 10.0
            ln = GcDbLine(GcGePoint3d(0, y, 10), GcGePoint3d(50, y, 10))
            ms.appendGcDbEntity(ln)
            ln.close()

        # 1 okrąg na Z=25 (uciekły)
        circ = GcDbCircle(GcGePoint3d(25, 25, 25), GcGeVector3d(0, 0, 1), 15)
        ms.appendGcDbEntity(circ)
        circ.close()

        ms.close()
        gcutPrintf("\n[SCENA_Z] Gotowe. 6 obiektow: 3 na Z=0, 3 poza Z=0.")
        gcutPrintf("\n[SCENA_Z] Teraz APPLOAD 26_audit_z_axis.py i wpisz AUDYTZ — ma wykryc 3.")

    except Exception as err:
        gcutPrintf("\n[SCENA_Z BLAD] %s: %s" % (type(err).__name__, str(err)))
