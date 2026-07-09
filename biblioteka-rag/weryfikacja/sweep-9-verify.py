# Sweep 9 — weryfikacja prymitywów wzorców 15-20, NIEINTERAKTYWNIE.
#
# Każdy test tworzy własną encję/plik w skrypcie i operuje po ObjectId — bez
# gcedEntSel, bez klikania, bez Alt+Tab (co eliminuje crash środowiskowy SP1/RDP).
# Odpalasz komendę, czekasz, czytasz wynik. Log też do pliku (flush) na wypadek
# crashu: C:\Users\rdp\Desktop\sweep9-progress.txt
#
# UŻYCIE — na świeżym rysunku (Ctrl+N), pojedynczo:
#   VERIFY_SYSVAR    — gcedGetVar + resbuf (wzorzec 16)
#   VERIFY_OFFSET    — GcDbEllipse.getOffsetCurves (wzorzec 18)
#   VERIFY_DEEPCLONE — deepCloneObjects + GcDbObjectIdArray + GcDbIdMapping (wzorzec 19)
#   VERIFY_XDATA     — gcdbRegApp + gcutNewRb resbuf + setXData + xData odczyt (wzorzec 20)
#   VERIFY_DWGRW     — GcDbDatabase saveAs + readDwgFile (wzorzec 17)
#   (wzorzec 15 = gcedGetKword: interaktywny; jego rysowanie to GcDbPolyline —
#    już zwalidowane. Keyword input standardowy, niski ryzyk.)
#   SWEEP9_ALL — wszystkie po kolei

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "sweep9-progress.txt")


def _log(msg, truncate=False):
    try:
        with open(LOG, "w" if truncate else "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
    try:
        gcutPrintf("\n" + msg)
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


@command(local_name='VERIFY_SYSVAR')
def verifySysvar():
    """wzorzec 16: gcedGetVar + resbuf dla różnych typów."""
    try:
        _log("=== SYSVAR start ===", truncate=True)
        res = []
        for name, typ in [("VIEWSIZE", "rreal"), ("PLINETYPE", "rint"),
                          ("CLAYER", "rstring"), ("LTSCALE", "rreal")]:
            try:
                rb = resbuf()
                gcedGetVar(name, rb)
                val = getattr(rb.resval, typ)
                res.append(f"{name}={val}")
            except Exception as e:
                res.append(f"{name}=NIE({type(e).__name__})")
        _log("[SWEEP9 SYSVAR] " + " | ".join(res))
    except Exception as err:
        _log(f"[SWEEP9 SYSVAR] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_OFFSET')
def verifyOffset():
    """wzorzec 18: utwórz elipsę, odsuń przez getOffsetCurves."""
    try:
        _log("=== OFFSET start ===", truncate=True)
        ms = _ms(GcDb.kForWrite)
        if ms is None:
            _log("[SWEEP9 OFFSET] FAIL: MS open")
            return
        # GcDbEllipse(center, normal, majorAxis, radiusRatio)
        try:
            el = GcDbEllipse(GcGePoint3d(0, 0, 0), GcGeVector3d(0, 0, 1),
                             GcGeVector3d(100, 0, 0), 0.5)
        except Exception as e:
            ms.close()
            _log(f"[SWEEP9 OFFSET] FAIL (konstruktor GcDbEllipse): {type(e).__name__}: {e}")
            return
        s, eid = ms.appendGcDbEntity(el)
        el.close()
        ms.close()

        s, obj = gcdbOpenObject(eid, GcDb.kForRead)
        if not obj.isKindOf(GcDbEllipse.desc()):
            obj.close()
            _log("[SWEEP9 OFFSET] FAIL: nie elipsa")
            return
        ellipse = GcDbEllipse.cast(obj)
        try:
            s, curves = ellipse.getOffsetCurves(10.0)
        except Exception as e:
            obj.close()
            _log(f"[SWEEP9 OFFSET] FAIL (getOffsetCurves): {type(e).__name__}: {e}")
            return
        obj.close()
        n = len(curves) if curves else 0
        # dodaj wynik do rysunku
        if n > 0:
            newE = GcDbEntity.cast(curves[0])
            ms = _ms(GcDb.kForWrite)
            ms.appendGcDbEntity(newE)
            ms.close()
            newE.close()
        _log(f"[SWEEP9 OFFSET] PASS — getOffsetCurves zwrócił {n} krzywych")
    except Exception as err:
        _log(f"[SWEEP9 OFFSET] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_DEEPCLONE')
def verifyDeepClone():
    """wzorzec 19: deepCloneObjects na utworzonym okręgu."""
    try:
        _log("=== DEEPCLONE start ===", truncate=True)
        ms = _ms(GcDb.kForWrite)
        if ms is None:
            _log("[SWEEP9 DEEPCLONE] FAIL: MS open")
            return
        c = GcDbCircle(GcGePoint3d(50, 50, 0), GcGeVector3d(0, 0, 1), 25.0)
        s, cid = ms.appendGcDbEntity(c)
        c.close()
        ms.close()

        db = gcdbWorkingDatabase()
        s, bt = db.getBlockTable(GcDb.kForRead)
        s, msId = bt.getObjIdAt(GCDB_MODEL_SPACE)
        bt.close()

        ids = GcDbObjectIdArray()
        ids.append(cid)
        idMap = GcDbIdMapping()
        try:
            s, pairs = db.deepCloneObjects(ids, msId, idMap, False)
        except Exception as e:
            _log(f"[SWEEP9 DEEPCLONE] FAIL (deepCloneObjects): {type(e).__name__}: {e}")
            return
        npairs = len(pairs) if pairs else 0
        _log(f"[SWEEP9 DEEPCLONE] PASS — status={s}, par w mapie={npairs}")
    except Exception as err:
        _log(f"[SWEEP9 DEEPCLONE] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_XDATA')
def verifyXData():
    """wzorzec 20: gcdbRegApp + gutNewRb resbuf + setXData + xData odczyt."""
    try:
        _log("=== XDATA start ===", truncate=True)
        kApp = 1001
        kStr = 1000
        APP = "TMSYS_SWEEP9"
        TXT = "test xdata"

        ms = _ms(GcDb.kForWrite)
        if ms is None:
            _log("[SWEEP9 XDATA] FAIL: MS open")
            return
        ln = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(100, 0, 0))
        s, lid = ms.appendGcDbEntity(ln)
        ln.close()
        ms.close()

        _log("PRZED: gcdbRegApp")
        gcdbRegApp(APP)
        _log("PRZED: budowa resbuf")
        rb = gcutNewRb(kApp)
        rb.resval.rstring = APP
        rb.rbnext = gcutNewRb(kStr)
        rb.rbnext.resval.rstring = TXT
        _log("PO: resbuf zbudowany")

        s, obj = gcdbOpenObject(lid, GcDb.kForWrite)
        _log("PRZED: setXData")
        obj.setXData(rb)
        _log("PO: setXData")
        obj.close()
        gcutRelRb(rb)

        # odczyt z powrotem
        s, obj2 = gcdbOpenObject(lid, GcDb.kForRead)
        rb2 = obj2.xData(APP)
        got = "brak"
        if rb2 is not None:
            p = rb2
            while p is not None:
                if p.restype == kStr:
                    got = p.resval.rstring
                p = p.rbnext
            gcutRelRb(rb2)
        obj2.close()
        ok = "OK" if got == TXT else f"ROZBIEZNOSC({got})"
        _log(f"[SWEEP9 XDATA] PASS — zapisano+odczytano: {ok}")
    except Exception as err:
        _log(f"[SWEEP9 XDATA] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_DWGRW')
def verifyDwgReadWrite():
    """wzorzec 17: zapis nowej bazy do DWG + odczyt z powrotem + iteracja."""
    try:
        _log("=== DWGRW start ===", truncate=True)
        path = os.path.join(os.path.expanduser("~"), "Desktop", "sweep9_test.dwg")

        # zapis
        dbW = GcDbDatabase(True, False)
        s, bt = dbW.getBlockTable(GcDb.kForRead)
        s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        bt.close()
        c1 = GcDbCircle(GcGePoint3d(1, 1, 0), GcGeVector3d(0, 0, 1), 1.0)
        ms.appendGcDbEntity(c1)
        c1.close()
        c2 = GcDbCircle(GcGePoint3d(4, 4, 0), GcGeVector3d(0, 0, 1), 1.0)
        ms.appendGcDbEntity(c2)
        c2.close()
        ms.close()
        if dbW.saveAs(path) != Gcad.eOk:
            _log("[SWEEP9 DWGRW] FAIL: saveAs != eOk")
            return
        _log("PO: saveAs OK")

        # odczyt
        dbR = GcDbDatabase(False, False)
        if dbR.readDwgFile(path) != Gcad.eOk:
            _log("[SWEEP9 DWGRW] FAIL: readDwgFile != eOk")
            return
        s, bt = dbR.getBlockTable(GcDb.kForRead)
        s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        s, it = ms.newIterator()
        it.start()
        n = 0
        while not it.done():
            s, ent = it.getEntity()
            if s == Gcad.eOk and ent is not None:
                n += 1
            it.step()
        ms.close()
        _log(f"[SWEEP9 DWGRW] PASS — zapis+odczyt OK, obiektów w pliku={n}")
    except Exception as err:
        _log(f"[SWEEP9 DWGRW] FAIL: {type(err).__name__}: {err}")


@command(local_name='SWEEP9_ALL')
def sweep9All():
    """Wszystkie testy po kolei (wszystkie nieinteraktywne)."""
    gcutPrintf("\n===== SWEEP9 START =====")
    verifySysvar()
    verifyOffset()
    verifyDeepClone()
    verifyXData()
    verifyDwgReadWrite()
    gcutPrintf("\n===== SWEEP9 KONIEC =====")
