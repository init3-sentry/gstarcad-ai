# Wzorcowa komenda 26 — Audyt osi Z: znajdź i podświetl obiekty „uciekłe" poza Z=0.
#
# Zamyka pozycję #11 z raportu Roberta. Realny ból geodety/projektanta 2D: część
# obiektów w rysunku ma współrzędną Z różną od zera (import z innego programu, błąd
# rysowania, blok wstawiony na wysokości). W rzucie z góry ich NIE WIDAĆ, ale:
#   - kursor „łapie" je na wysokości Z → pomiary (odległości/pola) wychodzą błędne,
#   - eksport/druk potrafi się rozjechać.
# GstarCAD sam tego nie sygnalizuje. Ta komenda robi audyt: przechodzi wszystkie
# obiekty modelu, liczy ich zakres Z z geometrii i PODŚWIETLA te poza płaszczyzną 2D.
#
# Uniwersalny detektor: getGeomExtents(ext) daje realny bounding-box encji (min/max
# punkt) — działa dla DOWOLNEJ encji (linia, polilinia, blok, tekst, okrąg…), nie
# trzeba znać jej typu ani szukać per-klasa metody elevation(). Jeśli |Zmin|>tol lub
# |Zmax|>tol → obiekt nie leży w płaszczyźnie 2D.
#
# Sposób użycia: APPLOAD → komenda AUDYTZ (skan + podświetlenie + raport w command
# line). Podświetlone zostają obiekty poza Z=0. Na koniec: AUDYTZ_OFF zdejmuje
# podświetlenie. Gdyby podświetlenie nie było widoczne od razu — wpisz REGEN.
#
# Konwencje domu: 3 importy, @command, całość w try/except, Gcad.eOk dla bazy,
# iteracja modelu jak wzorzec 12 (newIterator/start/done/step), getEntity(kForWrite)
# by móc podświetlić, ObjectId zapamiętany globalnie na późniejsze AUDYTZ_OFF.

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *

TOL_Z = 1e-6                 # poniżej tego traktujemy jako Z=0 (szum float)
MAX_LIST = 15               # ile pozycji wypisać szczegółowo w raporcie

_podswietlone = []          # lista GcDbObjectId encji podświetlonych ostatnim audytem


def _openModelSpaceIter():
    """Zwraca (ms, iterator) modelu, albo (None, None). ms otwarty do zapisu."""
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None, None
    # model otwieramy do zapisu — chcemy móc podświetlić encje w trakcie iteracji
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if status != Gcad.eOk:
        return None, None
    status, it = ms.newIterator()
    if status != Gcad.eOk:
        ms.close()
        return None, None
    return ms, it


def _zdejmij_podswietlenie():
    """Otwiera zapamiętane encje i zdejmuje z nich podświetlenie."""
    global _podswietlone
    ile = 0
    for oid in _podswietlone:
        try:
            status, obj = gcdbOpenObject(oid, GcDb.kForWrite)
            if status == Gcad.eOk and obj is not None:
                obj.unhighlight()
                obj.close()
                ile += 1
        except Exception:
            pass
    _podswietlone = []
    return ile


@command(local_name='AUDYTZ')
def audytz():
    """Skan całego modelu — podświetl i policz obiekty poza płaszczyzną Z=0."""
    try:
        # najpierw skasuj podświetlenie z poprzedniego audytu (idempotencja)
        _zdejmij_podswietlenie()

        ms, it = _openModelSpaceIter()
        if ms is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc przestrzeni modelu.")
            return

        total = 0
        flagged = 0
        szczegoly = []       # (klasa, zmin, zmax)

        it.start()
        while not it.done():
            status, ent = it.getEntity(GcDb.kForWrite)
            if status == Gcad.eOk and ent is not None:
                total += 1
                ext = GcDbExtents()
                st = ent.getGeomExtents(ext)
                if st == Gcad.eOk:
                    zmin = ext.minPoint().z
                    zmax = ext.maxPoint().z
                    if abs(zmin) > TOL_Z or abs(zmax) > TOL_Z:
                        flagged += 1
                        try:
                            klasa = ent.isA().name()
                        except Exception:
                            klasa = "(nieznany)"
                        try:
                            _podswietlone.append(ent.objectId())
                            ent.highlight()
                        except Exception:
                            pass
                        if len(szczegoly) < MAX_LIST:
                            szczegoly.append((klasa, zmin, zmax))
                ent.close()
            it.step()

        ms.close()

        # raport
        gcutPrintf("\n=== AUDYT OSI Z ===")
        gcutPrintf("\nPrzeskanowano obiektow: %d" % total)
        if flagged == 0:
            gcutPrintf("\nWszystko na plaszczyznie 2D (Z=0). Czysto.")
            return
        gcutPrintf("\nOBIEKTY POZA Z=0: %d  (podswietlone w rysunku)" % flagged)
        for klasa, zmin, zmax in szczegoly:
            if abs(zmin - zmax) < TOL_Z:
                gcutPrintf("\n  - %-24s Z=%.4f" % (klasa, zmin))
            else:
                gcutPrintf("\n  - %-24s Z od %.4f do %.4f" % (klasa, zmin, zmax))
        if flagged > MAX_LIST:
            gcutPrintf("\n  ... oraz %d wiecej." % (flagged - MAX_LIST))
        gcutPrintf("\nAby zdjac podswietlenie: AUDYTZ_OFF. Jesli nie widac - wpisz REGEN.")

    except Exception as err:
        gcutPrintf("\n[AUDYTZ BLAD] %s: %s" % (type(err).__name__, str(err)))


@command(local_name='AUDYTZ_OFF')
def audytz_off():
    """Zdejmij podświetlenie założone przez ostatni AUDYTZ."""
    try:
        ile = _zdejmij_podswietlenie()
        gcutPrintf("\n[AUDYTZ_OFF] Zdjeto podswietlenie z %d obiektow." % ile)
    except Exception as err:
        gcutPrintf("\n[AUDYTZ_OFF BLAD] %s: %s" % (type(err).__name__, str(err)))
