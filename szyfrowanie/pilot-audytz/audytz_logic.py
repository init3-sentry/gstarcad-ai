# -*- coding: utf-8 -*-
# Logika GSAI_AUDYTZ do skompilowania -> audytz_logic.pyd (Cython, cp311-win_amd64).
# NIE importuje pygcad: 'import *' nie wstrzykuje nazw do importowanego podmodulu
# (NameError w runtime). Loader (otwarty, APPLOAD-owany) ma API przez 'import *' i
# przekazuje CALE swoje globals() -> tu wstrzykujemy je do naszych globals, dalej kod
# uzywa nazw normalnie. Wzorzec skaluje sie na dowolna liczbe nazw API.
# Patrz: szyfrowanie/README-cython.md.

TOL_Z = 1e-6                 # ponizej tego traktujemy jako Z=0 (szum float)
MAX_LIST = 15                # ile pozycji wypisac szczegolowo w raporcie

# Nazwy API pygcad uzyte nizej — MUSZA byc zadeklarowane jako globalsy, bo Cython nie
# kompiluje bare undeclared nazw ("undeclared name not builtin"). Realne wartosci
# wstrzykuje run() przez globals().update(api) z loadera (patrz README-cython.md).
gcdbWorkingDatabase = GcDb = Gcad = GCDB_MODEL_SPACE = GcDbExtents = None
gds_name = gcdbHandEnt = gcedSSAdd = gcedSSSetFirst = gcutPrintf = None


def run(api):
    globals().update(api)    # API pygcad z loadera -> nasze globalsy
    _audytz()


def _audytz():
    """Wykryj i zaznacz (uchwyty) obiekty poza plaszczyzna Z=0. Splaszcza je natywny FLATTEN."""
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[AUDYTZ] Nie mozna otworzyc tabeli blokow.")
            return
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[AUDYTZ] Nie mozna otworzyc modelu.")
            return
        status, it = ms.newIterator()
        if status != Gcad.eOk:
            ms.close()
            gcutPrintf("\n[AUDYTZ] Nie mozna utworzyc iteratora.")
            return

        sset = gds_name()        # pusty bufor selection setu (pusty = utworz przy 1. SSAdd)
        total = 0
        poza = 0                 # ile obiektow poza Z=0 (wszystkie)
        dodane = 0               # ile realnie trafilo do selekcji
        szczegoly = []           # (klasa, zmin, zmax) do raportu, max MAX_LIST

        it.start()
        while not it.done():
            status, ent = it.getEntity()
            if status == Gcad.eOk and ent is not None:
                total += 1
                ext = GcDbExtents()
                st = ent.getGeomExtents(ext)
                if st == Gcad.eOk:
                    zmin = ext.minPoint().z
                    zmax = ext.maxPoint().z
                    if abs(zmin) > TOL_Z or abs(zmax) > TOL_Z:
                        poza += 1
                        try:
                            klasa = ent.isA().name()
                        except Exception:
                            klasa = "(nieznany)"
                        # most: handle -> ename -> selection set
                        try:
                            ok, hstr = ent.getGcDbHandle().getIntoAsciiBuffer()
                            if ok and hstr:
                                en = gds_name()
                                gcdbHandEnt(hstr, en)
                                gcedSSAdd(en, sset, sset)
                                dodane += 1
                        except Exception:
                            pass
                        if len(szczegoly) < MAX_LIST:
                            szczegoly.append((klasa, zmin, zmax))
                ent.close()
            it.step()
        ms.close()

        # raport + zaznaczenie
        gcutPrintf("\n=== AUDYT OSI Z (z .pyd) ===")
        gcutPrintf("\nPrzeskanowano obiektow: %d" % total)
        if poza == 0:
            gcutPrintf("\nWszystko na plaszczyznie 2D (Z=0). Czysto.")
            return

        # ustaw pickfirst — obiekty dostana uchwyty
        gcedSSSetFirst(sset, gds_name())

        gcutPrintf("\nOBIEKTY POZA Z=0: %d  (ZAZNACZONE, uchwyty w rysunku)" % poza)
        for klasa, zmin, zmax in szczegoly:
            if abs(zmin - zmax) < TOL_Z:
                gcutPrintf("\n  - %-24s Z=%.4f" % (klasa, zmin))
            else:
                gcutPrintf("\n  - %-24s Z od %.4f do %.4f  (3D)" % (klasa, zmin, zmax))
        if poza > MAX_LIST:
            gcutPrintf("\n  ... oraz %d wiecej." % (poza - MAX_LIST))
        gcutPrintf("\nAby SPLASZCZYC do Z=0: wpisz FLATTEN (splaszczy zaznaczone od reki).")
        gcutPrintf("\n(ESC zdejmuje uchwyty. 'Z od..do (3D)' = obiekt celowo rozciagniety w Z.)")

    except Exception as err:
        gcutPrintf("\n[AUDYTZ BLAD] %s: %s" % (type(err).__name__, str(err)))
