# Sweep 8 — STRESS / SOAK test do reprodukcji crashu dla GstarSoft R&D.
#
# Cel: znaleźć deterministyczny, autonomiczny (bez klikania) scenariusz, który
# crashuje GstarCAD-a, żeby wysłać czysty raport do R&D. Hipoteza Dawida:
# "coś strzela w pamięć i kumuluje się po jakimś czasie". Ten skrypt hamruje
# operacje pygcad w pętlach po tysiące iteracji i loguje postęp do PLIKU z
# natychmiastowym zamknięciem (flush na dysk). Po crashu do pulpitu plik
# pokazuje OSTATNIĄ ukończoną iterację i którą operację hamrowaliśmy.
#
# Log: C:\Users\rdp\Desktop\sweep8-stress.txt  (albo ~/Desktop)
#
# UŻYCIE — każdą komendę na ŚWIEŻYM rysunku (Ctrl+N przed każdą), pojedynczo:
#   STRESS_OPENCLOSE  — pętla open/close tabel (bez tworzenia encji) — czysta churn tabel
#   STRESS_CREATE     — pętla tworzenia encji (okrąg+linia) w model space
#   STRESS_ITER       — pętla iteracji po model space + isA().name()
#   STRESS_LAYER      — pętla tworzenia/odczytu warstw
#   STRESS_MIXED      — realistyczny mix per iteracja (create+iter+layer+read)
#   STRESS_2DPOLY     — PODEJRZANY: programowa konstrukcja GcDb2dPolyline (mało iteracji)
#
# Po crashu: NIE przepisuj nic — Dawid mówi "crash", ja czytam plik przez SSH.
# Jak przejdzie bez crashu — ostatnia linia "=== ... BEZ crashu ===".

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "sweep8-stress.txt")


def _log(msg, truncate=False):
    try:
        with open(LOG, "w" if truncate else "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def _ms(mode):
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return None
    s, ms = bt.getAt(GCDB_MODEL_SPACE, mode)
    bt.close()
    return ms if s == Gcad.eOk else None


@command(local_name='STRESS_OPENCLOSE')
def stressOpenClose():
    """Czysta churn otwierania/zamykania tabel — bez tworzenia encji.
    Izoluje hipotezę 'wyciek uchwytów tabel kumuluje się'."""
    N = 5000
    _log(f"=== STRESS_OPENCLOSE start N={N} ===", truncate=True)
    try:
        db = gcdbWorkingDatabase()
        for i in range(N):
            s, bt = db.getBlockTable(GcDb.kForRead)
            if s == Gcad.eOk:
                bt.close()
            s, lt = db.getLayerTable(GcDb.kForRead)
            if s == Gcad.eOk:
                lt.close()
            if i % 100 == 0:
                _log(f"i={i} ok")
        _log(f"=== STRESS_OPENCLOSE koniec: {N} iteracji BEZ crashu ===")
        gcutPrintf(f"\n[STRESS_OPENCLOSE] {N} iteracji BEZ crashu")
    except Exception as e:
        _log(f"WYJATEK: {type(e).__name__}: {e}")


@command(local_name='STRESS_CREATE')
def stressCreate():
    """Churn tworzenia encji (okrąg + linia) w model space."""
    N = 3000
    _log(f"=== STRESS_CREATE start N={N} ===", truncate=True)
    try:
        for i in range(N):
            ms = _ms(GcDb.kForWrite)
            if ms is None:
                _log(f"i={i}: MS open != eOk (moze zatruta sesja)")
                return
            c = GcDbCircle(GcGePoint3d(float(i % 1000), float(i % 700), 0.0), GcGeVector3d(0, 0, 1), 5.0)
            ms.appendGcDbEntity(c)
            c.close()
            l = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(float(i % 500), 10.0, 0))
            ms.appendGcDbEntity(l)
            l.close()
            ms.close()
            if i % 100 == 0:
                _log(f"i={i} ok")
        _log(f"=== STRESS_CREATE koniec: {N} iteracji BEZ crashu ===")
        gcutPrintf(f"\n[STRESS_CREATE] {N} iteracji BEZ crashu")
    except Exception as e:
        _log(f"WYJATEK: {type(e).__name__}: {e}")


@command(local_name='STRESS_ITER')
def stressIter():
    """Churn iteracji po model space + isA().name(). Najpierw dodaje 200 encji,
    potem iteruje je N razy — hamruje newIterator/getEntity/isA."""
    N = 2000
    _log(f"=== STRESS_ITER start N={N} ===", truncate=True)
    try:
        ms = _ms(GcDb.kForWrite)
        if ms is None:
            _log("MS open != eOk (setup)")
            return
        for k in range(200):
            c = GcDbCircle(GcGePoint3d(float(k), float(k), 0), GcGeVector3d(0, 0, 1), 2.0)
            ms.appendGcDbEntity(c)
            c.close()
        ms.close()
        _log("setup: 200 encji dodane")

        for i in range(N):
            ms = _ms(GcDb.kForRead)
            if ms is None:
                _log(f"i={i}: MS reopen != eOk")
                return
            s, it = ms.newIterator()
            if s != Gcad.eOk:
                ms.close()
                _log(f"i={i}: newIterator != eOk")
                return
            it.start()
            cnt = 0
            while not it.done():
                s, ent = it.getEntity()
                if s == Gcad.eOk and ent is not None:
                    try:
                        _ = ent.isA().name()
                    except Exception:
                        pass
                    cnt += 1
                it.step()
            ms.close()
            if i % 50 == 0:
                _log(f"i={i} przeiterowano={cnt}")
        _log(f"=== STRESS_ITER koniec: {N} iteracji BEZ crashu ===")
        gcutPrintf(f"\n[STRESS_ITER] {N} iteracji BEZ crashu")
    except Exception as e:
        _log(f"WYJATEK: {type(e).__name__}: {e}")


@command(local_name='STRESS_LAYER')
def stressLayer():
    """Churn tworzenia i odczytu warstw (getLayerTable kForWrite/read + add + iter)."""
    N = 1000
    _log(f"=== STRESS_LAYER start N={N} ===", truncate=True)
    try:
        db = gcdbWorkingDatabase()
        for i in range(N):
            s, lt = db.getLayerTable(GcDb.kForWrite)
            if s != Gcad.eOk:
                _log(f"i={i}: getLayerTable(W) != eOk")
                return
            name = f"STRESS_L{i}"
            if not lt.has(name):
                rec = GcDbLayerTableRecord()
                rec.setName(name)
                col = GcCmColor()
                col.setColorIndex((i % 7) + 1)
                rec.setColor(col)
                lt.add(rec)
                rec.close()
            lt.close()
            if i % 50 == 0:
                _log(f"i={i} ok")
        _log(f"=== STRESS_LAYER koniec: {N} warstw BEZ crashu ===")
        gcutPrintf(f"\n[STRESS_LAYER] {N} warstw BEZ crashu")
    except Exception as e:
        _log(f"WYJATEK: {type(e).__name__}: {e}")


@command(local_name='STRESS_MIXED')
def stressMixed():
    """Realistyczny mix per iteracja: utwórz encję + iteruj + operacja na warstwie.
    Najbliższe 'szeregowi działań' z realnego użycia. N mniejsze bo iteracja rośnie."""
    N = 800
    _log(f"=== STRESS_MIXED start N={N} ===", truncate=True)
    try:
        db = gcdbWorkingDatabase()
        for i in range(N):
            # create
            ms = _ms(GcDb.kForWrite)
            if ms is None:
                _log(f"i={i}: MS open != eOk")
                return
            c = GcDbCircle(GcGePoint3d(float(i % 300), float(i % 200), 0), GcGeVector3d(0, 0, 1), 3.0)
            ms.appendGcDbEntity(c)
            c.close()
            ms.close()
            # iterate
            ms = _ms(GcDb.kForRead)
            s, it = ms.newIterator()
            it.start()
            cnt = 0
            while not it.done():
                s, ent = it.getEntity()
                if s == Gcad.eOk and ent is not None:
                    cnt += 1
                it.step()
            ms.close()
            # layer op
            s, lt = db.getLayerTable(GcDb.kForRead)
            if s == Gcad.eOk:
                lt.close()
            if i % 50 == 0:
                _log(f"i={i} encji_w_MS={cnt}")
        _log(f"=== STRESS_MIXED koniec: {N} iteracji BEZ crashu ===")
        gcutPrintf(f"\n[STRESS_MIXED] {N} iteracji BEZ crashu")
    except Exception as e:
        _log(f"WYJATEK: {type(e).__name__}: {e}")


@command(local_name='STRESS_2DPOLY')
def stress2dPoly():
    """PODEJRZANY: programowa konstrukcja GcDb2dPolyline (to co crashowało w SWEEP6).
    Mało iteracji — jeśli crashuje deterministycznie, plik pokaże na której.
    Testuje sekwencję: GcDb2dPolyline() -> append do MS -> GcDb2dVertex+appendVertex."""
    N = 20
    _log(f"=== STRESS_2DPOLY start N={N} ===", truncate=True)
    try:
        for i in range(N):
            _log(f"i={i}: PRZED konstrukcji GcDb2dPolyline")
            ms = _ms(GcDb.kForWrite)
            if ms is None:
                _log(f"i={i}: MS open != eOk")
                return
            poly = GcDb2dPolyline()
            _log(f"i={i}: PO GcDb2dPolyline(), PRZED append do MS")
            s, pid = ms.appendGcDbEntity(poly)
            _log(f"i={i}: PO append do MS (status={s}), PRZED appendVertex")
            for (x, y) in [(0, 0), (100, 0), (100, 50)]:
                v = GcDb2dVertex()
                v.setPosition(GcGePoint3d(float(x), float(y), 0.0))
                poly.appendVertex(v)
                v.close()
            _log(f"i={i}: PO appendVertex (3 wierzchołki)")
            poly.close()
            ms.close()
            _log(f"i={i}: OK cała iteracja")
        _log(f"=== STRESS_2DPOLY koniec: {N} iteracji BEZ crashu ===")
        gcutPrintf(f"\n[STRESS_2DPOLY] {N} iteracji BEZ crashu")
    except Exception as e:
        _log(f"WYJATEK (NIE crash): {type(e).__name__}: {e}")
