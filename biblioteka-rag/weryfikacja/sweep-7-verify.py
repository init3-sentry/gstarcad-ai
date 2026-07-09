# Sweep 7 — IZOLACJA crashu odczytu polilinii (wzorzec 13 / VERIFY_2DPOLY).
#
# Problem: odczyt wierzchołków polilinii crashuje GstarCAD do pulpitu (SP1 też).
# Crash do pulpitu zabija konsolę, więc nie widać na czym stanął. Rozwiązanie:
# każdy krok logujemy do PLIKU na Pulpicie z natychmiastowym zamknięciem (flush).
# Po crashu odczytujemy plik — ostatnia linia "PRZED: X" bez pary "PO: X" wskazuje
# dokładnie wywołanie, które crashuje.
#
# Dodatkowo: polilinię znajdujemy przez ITERACJĘ MODEL SPACE (już potwierdzone
# jako bezpieczne w sweep-6 MSITER), NIE przez gcedEntSel — usuwamy z równania
# selekcję i Escape.
#
# PRZYGOTOWANIE (raz, przed testami):
#   1. SETVAR PLINETYPE 0
#   2. narysuj polilinię: PLINE, kliknij 3-4 punkty, Enter
#
# Sposób użycia:
#   VERIFY_PLINE_TYPE       — BEZPIECZNE: wypisuje klasy wszystkich obiektów
#                             (isA().name() — sprawdzone). Mówi czym jest narysowana
#                             polilinia: AcDb2dPolyline (ciężka) czy AcDbPolyline (lekka).
#   VERIFY_PLINE_READ_STEP  — instrumentowany odczyt krok-po-kroku, log do pliku
#                             C:\Users\rdp\Desktop\sweep7-progress.txt (albo ~/Desktop).
#                             Jeśli crashuje — czytamy ten plik.

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "sweep7-progress.txt")


def _log(msg, truncate=False):
    """Zapis do pliku z natychmiastowym zamknięciem (flush na dysk) + do konsoli."""
    try:
        mode = "w" if truncate else "a"
        with open(LOG, mode, encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
    try:
        gcutPrintf("\n" + msg)
    except Exception:
        pass


def _openModelSpaceRead():
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if status != Gcad.eOk:
        return None
    return ms


@command(local_name='VERIFY_PLINE_TYPE')
def verifyPlineType():
    """BEZPIECZNE: wypisz klasę każdego obiektu w model space (tylko isA().name())."""
    try:
        _log("=== PLINE_TYPE start ===", truncate=True)
        ms = _openModelSpaceRead()
        if ms is None:
            _log("FAIL: nie otwarto model space")
            return
        status, it = ms.newIterator()
        if status != Gcad.eOk:
            ms.close()
            _log("FAIL: newIterator")
            return
        n = 0
        it.start()
        while not it.done():
            status, ent = it.getEntity()
            if status == Gcad.eOk and ent is not None:
                try:
                    nm = ent.isA().name()
                except Exception as e:
                    nm = f"(brak isA: {type(e).__name__})"
                _log(f"obiekt[{n}] = {nm}")
                n += 1
            it.step()
        ms.close()
        _log(f"=== PLINE_TYPE koniec: {n} obiektów ===")
    except Exception as err:
        _log(f"FAIL PLINE_TYPE: {type(err).__name__}: {err}")


@command(local_name='VERIFY_PLINE_READ_STEP')
def verifyPlineReadStep():
    """Instrumentowany odczyt wierzchołków — log PRZED/PO każdym wywołaniu do pliku.
    Znajduje polilinię przez iterację model space (bez gcedEntSel)."""
    try:
        _log("=== READ_STEP start ===", truncate=True)
        ms = _openModelSpaceRead()
        if ms is None:
            _log("FAIL: nie otwarto model space")
            return
        status, it = ms.newIterator()
        if status != Gcad.eOk:
            ms.close()
            _log("FAIL: newIterator")
            return

        # znajdź pierwszą polilinię (2d LUB lekką) po nazwie klasy — bez isKindOf jeszcze
        target = None
        target_cls = None
        it.start()
        while not it.done():
            status, ent = it.getEntity()
            if status == Gcad.eOk and ent is not None:
                try:
                    nm = ent.isA().name()
                except Exception:
                    nm = ""
                if "Polyline" in nm or "2dPolyline" in nm:
                    target = ent
                    target_cls = nm
                    break
            it.step()

        if target is None:
            ms.close()
            _log("FAIL: nie znaleziono polilinii w model space (narysuj PLINE, PLINETYPE 0)")
            return

        _log(f"[1] znaleziono: {target_cls}")

        _log("PRZED: isKindOf(GcDb2dPolyline.desc())")
        is2d = target.isKindOf(GcDb2dPolyline.desc())
        _log(f"PO: isKindOf(GcDb2dPolyline) = {is2d}")

        _log("PRZED: isKindOf(GcDbPolyline.desc())")
        isLite = target.isKindOf(GcDbPolyline.desc())
        _log(f"PO: isKindOf(GcDbPolyline) = {isLite}")

        if not is2d:
            ms.close()
            _log("STOP: to nie GcDb2dPolyline — wzorzec 13 by tu wyszedł bez odczytu. "
                 "Jeśli crash był wcześniej, wina po stronie gcedEntSel, nie odczytu.")
            return

        _log("PRZED: vertexIterator()")
        vit = target.vertexIterator()
        _log("PO: vertexIterator()")

        _log("PRZED: vit.done() [pierwsze]")
        done = vit.done()
        _log(f"PO: vit.done() = {done}")

        step = 0
        while not vit.done() and step < 100:
            _log(f"--- wierzchołek {step} ---")
            _log("PRZED: vit.objectId()")
            vid = vit.objectId()
            _log("PO: vit.objectId()")

            _log("PRZED: gcdbOpenObject(vertex)")
            status, vo = gcdbOpenObject(vid, GcDb.kForRead)
            _log(f"PO: gcdbOpenObject(vertex) status={status}")

            _log("PRZED: GcDb2dVertex.cast()")
            vtx = GcDb2dVertex.cast(vo)
            _log("PO: GcDb2dVertex.cast()")

            _log("PRZED: vtx.position()")
            p = vtx.position()
            _log(f"PO: vtx.position() = ({p.x:.2f}, {p.y:.2f}, {p.z:.2f})")

            _log("PRZED: vtx.close()")
            vtx.close()
            _log("PO: vtx.close()")

            _log("PRZED: vit.step()")
            vit.step()
            _log("PO: vit.step()")
            step += 1

        ms.close()
        _log(f"=== READ_STEP koniec: odczytano {step} wierzchołków BEZ crashu ===")
    except Exception as err:
        _log(f"FAIL READ_STEP (wyjątek, NIE crash): {type(err).__name__}: {err}")
