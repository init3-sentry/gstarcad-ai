# Diagnostyka eNotOpenForWrite w batch find-replace (wzorzec 21).
# Samowystarczalny: seeduje dane, potem robi zamiane BETA->GAMMA z GRANULARNYM
# logowaniem KAZDEGO wywolania API (open/get/set) -> pinpoint gdzie leci blad.
# Log (flush per linia, przezywa crash/modal): Desktop\diag-replace.txt
#
# UZYCIE (nowy pusty rysunek): APPLOAD -> diag-replace.py -> DIAG_ZAMIEN

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "diag-replace.txt")


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


def _try(label, fn):
    """Wywolaj fn(), zaloguj wynik lub wyjatek. Zwraca (ok, wartosc)."""
    try:
        v = fn()
        _log(f"    {label} = OK -> {repr(v)}")
        return True, v
    except Exception as e:
        _log(f"    {label} = WYJATEK ({type(e).__name__}: {e})")
        return False, None


def _ms(mode):
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return None
    s, ms = bt.getAt(GCDB_MODEL_SPACE, mode)
    bt.close()
    return ms if s == Gcad.eOk else None


def _seed():
    _log("--- SEED ---")
    ms = _ms(GcDb.kForWrite)
    t = GcDbText(GcGePoint3d(0, 0, 0), "BETA-999")
    ms.appendGcDbEntity(t)
    t.close()
    m = GcDbMText()
    m.setLocation(GcGePoint3d(0, 50, 0))
    m.setContents("MTEXT-BETA")
    ms.appendGcDbEntity(m)
    m.close()
    ms.close()
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForWrite)
    if not bt.has("DIAG_BLK"):
        bd = GcDbBlockTableRecord()
        bd.setName("DIAG_BLK")
        bt.add(bd)
        ad = GcDbAttributeDefinition()
        ad.setTextString("DEFAULT")
        ad.setTag("NUMER")
        ad.setPosition(GcGePoint3d(0, 0, 0))
        ad.setHeight(2.5)
        bd.appendGcDbEntity(ad)
        ad.close()
        bd.close()
    s, bid = bt.getObjIdAt("DIAG_BLK")
    bt.close()
    ms2 = _ms(GcDb.kForWrite)
    ref = GcDbBlockReference(GcGePoint3d(100, 100, 0), bid)
    ms2.appendGcDbEntity(ref)
    attr = GcDbAttribute()
    attr.setTag("NUMER")
    attr.setTextString("A-001")
    attr.setPosition(GcGePoint3d(100, 100, 0))
    attr.setHeight(2.5)
    ref.appendAttribute(attr)
    attr.close()
    ref.close()
    ms2.close()
    _log("  seed OK: BETA-999, MTEXT-BETA, DIAG_BLK+NUMER=A-001")


def _collect_oids():
    ids = []
    ms = _ms(GcDb.kForRead)
    if ms is None:
        _log("  FAIL: MS(read)")
        return ids
    s, it = ms.newIterator()
    it.start()
    while not it.done():
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                cls = ent.isA().name()
            except Exception:
                cls = "?"
            try:
                ids.append((ent.objectId(), cls))
            except Exception:
                pass
            ent.close()
        it.step()
    ms.close()
    _log(f"  zebrano oids: {[c for _, c in ids]}")
    return ids


@command(local_name='DIAG_ZAMIEN')
def diagZamien():
    find, repl = "BETA", "GAMMA"
    try:
        _log("===== DIAG_ZAMIEN START =====", truncate=True)
        _seed()
        _log("--- FAZA ZAMIANY (granularnie) ---")
        for i, (oid, cls) in enumerate(_collect_oids()):
            _log(f"[{i}] klasa={cls}")
            ok, ent = _try(f"[{i}] gcdbOpenObject(kForWrite)", lambda: gcdbOpenObject(oid, GcDb.kForWrite))
            if not ok or ent is None:
                continue
            # gcdbOpenObject zwraca (status, obj) — rozpakuj
            status, obj = ent
            _log(f"    -> status={status}, obj={obj is not None}")
            if status != Gcad.eOk or obj is None:
                continue
            if "Text" in cls and "Attribute" not in cls:
                _, cur = _try(f"[{i}] _get textStringConst/text/contents", lambda: _read_any(obj))
                if cur and find in cur:
                    _try(f"[{i}] setTextString/setContents('{cur.replace(find, repl)}')",
                         lambda: _write_any(obj, cur.replace(find, repl)))
                else:
                    _log(f"    (brak '{find}' w {repr(cur)})")
            elif "BlockReference" in cls:
                _diag_blockref(i, obj, find, repl)
            _try(f"[{i}] obj.close()", lambda: obj.close())
        _log("===== DIAG_ZAMIEN KONIEC =====")
    except Exception as err:
        _log(f"[BLAD TOP] {type(err).__name__}: {err}")


def _read_any(ent):
    for g in ("textStringConst", "text", "contents"):
        fn = getattr(ent, g, None)
        if fn is None:
            continue
        v = fn()
        if isinstance(v, str):
            return v
    return None


def _write_any(ent, s):
    for st in ("setTextString", "setContents"):
        fn = getattr(ent, st, None)
        if fn is None:
            continue
        return f"{st}->{fn(s)}"
    return "brak-settera"


def _diag_blockref(i, ref, find, repl):
    ok, ait = _try(f"[{i}] ref.attributeIterator()", lambda: ref.attributeIterator())
    if not ok or ait is None:
        return
    k = 0
    while not ait.done():
        aid = ait.objectId()
        _log(f"  [{i}.{k}] atrybut aid")
        ok2, res = _try(f"  [{i}.{k}] ref.openAttribute(kForWrite)", lambda: ref.openAttribute(aid, GcDb.kForWrite))
        if ok2 and res is not None:
            sa, attr = res
            _log(f"      -> status={sa}, attr={attr is not None}")
            if sa == Gcad.eOk and attr is not None:
                _try(f"  [{i}.{k}] attr.tag()", lambda: attr.tag())
                _, cur = _try(f"  [{i}.{k}] attr._read", lambda: _read_any(attr))
                if cur and find in cur:
                    _try(f"  [{i}.{k}] attr._write", lambda: _write_any(attr, cur.replace(find, repl)))
                else:
                    _log(f"      (brak '{find}' w {repr(cur)})")
                _try(f"  [{i}.{k}] attr.close()", lambda: attr.close())
        ait.step()
        k += 1
