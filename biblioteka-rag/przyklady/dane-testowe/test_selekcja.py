# PROBE (nie wzorzec) — czy da się z pygcad ZAZNACZYĆ znalezione obiekty do pickfirst,
# tak żeby natywny FLATTEN od razu na nich zadziałał.
#
# Most do sprawdzenia: GcDbEntity -> handle (getGcDbHandle.getIntoAsciiBuffer) ->
# ename (gcdbHandEnt) -> selection set (gcedSSAdd) -> pickfirst (gcedSSSetFirst).
# To ten sam „głęboki ADS", co sortents/saveAs — może być pygcadowa luka. Probe rozstrzyga.
#
# Użycie na scenie z uciekłymi w Z obiektami: APPLOAD -> TESTSEL. Jeśli obiekty poza Z=0
# pokażą się ZAZNACZONE (uchwyty/gripsy) — most działa; wtedy wpisz FLATTEN i powinien
# od razu operować na tej selekcji (bez ręcznego wybierania).
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *

TOL_Z = 1e-6


@command(local_name='TESTSEL')
def testsel():
    """Zaznacz (pickfirst) obiekty poza Z=0 — test mostu selekcji pod FLATTEN."""
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[TESTSEL] Nie mozna otworzyc tabeli blokow.")
            return
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[TESTSEL] Nie mozna otworzyc modelu.")
            return
        status, it = ms.newIterator()
        if status != Gcad.eOk:
            ms.close()
            gcutPrintf("\n[TESTSEL] Nie mozna utworzyc iteratora.")
            return

        sset = gds_name()          # pusty bufor setu; pusty na starcie = "utwórz nowy set"
        dodane = 0

        it.start()
        while not it.done():
            status, ent = it.getEntity()
            if status == Gcad.eOk and ent is not None:
                ext = GcDbExtents()
                st = ent.getGeomExtents(ext)
                if st == Gcad.eOk:
                    if abs(ext.minPoint().z) > TOL_Z or abs(ext.maxPoint().z) > TOL_Z:
                        # obiekt poza Z=0 — złóż most handle -> ename -> selection set
                        try:
                            ok, hstr = ent.getGcDbHandle().getIntoAsciiBuffer()
                            if ok and hstr:
                                en = gds_name()
                                rc = gcdbHandEnt(hstr, en)
                                # pusty sset = utwórz nowy set; kolejne wywołania dokładają do niego
                                ss_rc = gcedSSAdd(en, sset, sset)
                                gcutPrintf("\n[TESTSEL] handle=%s gcdbHandEnt=%s SSAdd=%s"
                                           % (hstr, str(rc), str(ss_rc)))
                                dodane += 1
                        except Exception as e2:
                            gcutPrintf("\n[TESTSEL] most padl na obiekcie: %s: %s"
                                       % (type(e2).__name__, str(e2)))
                ent.close()
            it.step()
        ms.close()

        if dodane == 0:
            gcutPrintf("\n[TESTSEL] Zero obiektow poza Z=0 (albo most nie zadzialal). Uruchom najpierw SCENA_Z.")
            return

        status, length = gcedSSLength(sset)
        gcutPrintf("\n[TESTSEL] Do setu dodano %d, gcedSSLength=%s (rc=%s)" % (dodane, str(length), str(status)))

        first_rc = gcedSSSetFirst(sset, gds_name())   # 2. arg „unused" i tak musi być buforem, nie None
        gcutPrintf("\n[TESTSEL] gcedSSSetFirst rc=%s" % str(first_rc))
        gcutPrintf("\n[TESTSEL] >>> Czy obiekty poza Z=0 sa TERAZ ZAZNACZONE (uchwyty)? Jesli tak - most dziala, FLATTEN zadziala na nich od razu.")
        # NIE zwalniamy setu (gcedSSFree), bo pickfirst ma go trzymać do FLATTEN

    except Exception as err:
        gcutPrintf("\n[TESTSEL BLAD] %s: %s" % (type(err).__name__, str(err)))
