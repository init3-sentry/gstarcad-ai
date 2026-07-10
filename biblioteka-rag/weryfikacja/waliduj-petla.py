# Petlowy stress-test 3 wzorcow workhorse (21/22/23) + probe API handle.
# Seeduje RAZ, potem N iteracji: reset danych do bazy -> ZAMIEN(oczek.2) ->
# EKSPORT(1) -> RENUMERUJ(1) -> readback. Liczy PASS/FAIL. Na koncu probuje formy
# handle, zeby dobic bug eksportu. Log (flush per linia): Desktop\waliduj-petla.txt
#
# UZYCIE (NOWY pusty rysunek): APPLOAD -> waliduj-petla.py -> WALIDUJ_PETLA

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "waliduj-petla.txt")
N = 10


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


def _get_str(ent):
    for g in ("textStringConst", "text", "contents"):
        fn = getattr(ent, g, None)
        if fn is None:
            continue
        try:
            v = fn()
            if isinstance(v, str):
                return v
        except Exception:
            continue
    return None


def _set_str(ent, s):
    for st in ("setTextString", "setContents"):
        fn = getattr(ent, st, None)
        if fn is None:
            continue
        try:
            fn(s)
            return True
        except Exception:
            continue
    return False


def _collect():
    ids = []
    ms = _ms(GcDb.kForRead)
    if ms is None:
        return ids
    s, it = ms.newIterator()
    it.start()
    while not it.done():
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                ids.append((ent.objectId(), ent.isA().name()))
            except Exception:
                pass
            ent.close()
        it.step()
    ms.close()
    return ids


def _seed():
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
    if not bt.has("PETLA_BLK"):
        bd = GcDbBlockTableRecord()
        bd.setName("PETLA_BLK")
        bt.add(bd)
        ad = GcDbAttributeDefinition()
        ad.setTextString("DEFAULT")
        ad.setTag("NUMER")
        ad.setPosition(GcGePoint3d(0, 0, 0))
        ad.setHeight(2.5)
        bd.appendGcDbEntity(ad)
        ad.close()
        bd.close()
    s, bid = bt.getObjIdAt("PETLA_BLK")
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


def _each_attr(ref, mode, fn):
    """Iteruj atrybuty referencji, wywolaj fn(attr) na kazdym (attr otwarty w 'mode')."""
    try:
        it = ref.attributeIterator()
        while not it.done():
            aid = it.objectId()
            sa, a = ref.openAttribute(aid, mode)
            if sa == Gcad.eOk and a is not None:
                fn(a)
                a.close()
            it.step()
    except Exception:
        pass


def _reset():
    for oid, cls in _collect():
        s, ent = gcdbOpenObject(oid, GcDb.kForWrite)
        if s != Gcad.eOk or ent is None:
            continue
        if "Text" in cls and "Attribute" not in cls:
            _set_str(ent, "MTEXT-BETA" if "MText" in cls else "BETA-999")
        elif "BlockReference" in cls:
            def _r(a):
                if a.tag() == "NUMER":
                    _set_str(a, "A-001")
            _each_attr(ent, GcDb.kForWrite, _r)
        ent.close()


def _replace(find, repl):
    n = [0]
    for oid, cls in _collect():
        s, ent = gcdbOpenObject(oid, GcDb.kForWrite)
        if s != Gcad.eOk or ent is None:
            continue
        if "Text" in cls and "Attribute" not in cls:
            cur = _get_str(ent)
            if cur and find in cur and _set_str(ent, cur.replace(find, repl)):
                n[0] += 1
        elif "BlockReference" in cls:
            def _r(a):
                cur = _get_str(a)
                if cur and find in cur and _set_str(a, cur.replace(find, repl)):
                    n[0] += 1
            _each_attr(ent, GcDb.kForWrite, _r)
        ent.close()
    return n[0]


def _export():
    rows = [0]
    for oid, cls in _collect():
        if "BlockReference" not in cls:
            continue
        s, ref = gcdbOpenObject(oid, GcDb.kForRead)
        if s != Gcad.eOk or ref is None:
            continue
        _each_attr(ref, GcDb.kForRead, lambda a: rows.__setitem__(0, rows[0] + 1))
        ref.close()
    return rows[0]


def _renumber(tag, prefix, start, step):
    st = {"cur": start, "n": 0}
    for oid, cls in _collect():
        if "BlockReference" not in cls:
            continue
        s, ref = gcdbOpenObject(oid, GcDb.kForWrite)
        if s != Gcad.eOk or ref is None:
            continue
        def _r(a):
            if a.tag() == tag and _set_str(a, prefix + str(st["cur"]).zfill(3)):
                st["cur"] += step
                st["n"] += 1
        _each_attr(ref, GcDb.kForWrite, _r)
        ref.close()
    return st["n"]


def _readback():
    vals = {"t": None, "m": None, "a": None}
    for oid, cls in _collect():
        s, ent = gcdbOpenObject(oid, GcDb.kForRead)
        if s != Gcad.eOk or ent is None:
            continue
        if "MText" in cls:
            vals["m"] = _get_str(ent)
        elif "Text" in cls and "Attribute" not in cls:
            vals["t"] = _get_str(ent)
        elif "BlockReference" in cls:
            def _r(a):
                if a.tag() == "NUMER":
                    vals["a"] = _get_str(a)
            _each_attr(ent, GcDb.kForRead, _r)
        ent.close()
    return vals["t"], vals["m"], vals["a"]


def _handle_probe():
    _log("--- HANDLE PROBE ---")
    for oid, cls in _collect():
        if "BlockReference" not in cls:
            continue
        s, ref = gcdbOpenObject(oid, GcDb.kForRead)
        if s != Gcad.eOk or ref is None:
            continue
        try:
            h = ref.handle()
            _log(f"  ref.handle() repr -> {repr(h)}")
            _log(f"  str(ref.handle()) -> {repr(str(h))}")
            try:
                _log(f"  handle().getIntoAsciiBuffer() -> {repr(h.getIntoAsciiBuffer())}")
            except Exception as e:
                _log(f"  getIntoAsciiBuffer WYJATEK {type(e).__name__}: {e}")
            for meth in ("ascii", "asciiString", "getString", "toString"):
                fn = getattr(h, meth, None)
                if fn is not None:
                    try:
                        _log(f"  handle().{meth}() -> {repr(fn())}")
                    except Exception as e:
                        _log(f"  handle().{meth}() WYJATEK {e}")
        except Exception as e:
            _log(f"  ref.handle() WYJATEK {type(e).__name__}: {e}")
        try:
            h2 = ref.getGcDbHandle()
            _log(f"  ref.getGcDbHandle() str -> {repr(str(h2))}")
            try:
                _log(f"  getGcDbHandle().getIntoAsciiBuffer() -> {repr(h2.getIntoAsciiBuffer())}")
            except Exception as e:
                _log(f"  getGcDbHandle().getIntoAsciiBuffer WYJATEK {e}")
        except Exception as e:
            _log(f"  ref.getGcDbHandle() WYJATEK {type(e).__name__}: {e}")
        ref.close()
        break


@command(local_name='WALIDUJ_PETLA')
def walidujPetla():
    try:
        _log(f"===== WALIDUJ_PETLA START (N={N}) =====", truncate=True)
        _seed()
        ok_iters = 0
        for i in range(1, N + 1):
            _reset()
            r = _replace("BETA", "GAMMA")
            e = _export()
            rn = _renumber("NUMER", "P-", 1, 1)
            tv, mv, av = _readback()
            ok = (r == 2 and e == 1 and rn == 1 and tv == "GAMMA-999"
                  and mv == "MTEXT-GAMMA" and av == "P-001")
            if ok:
                ok_iters += 1
            _log(f"  iter {i}: replace={r}(2) export={e}(1) renumber={rn}(1) "
                 f"text={tv!r} mtext={mv!r} attr={av!r} -> {'PASS' if ok else 'FAIL'}")
        _log(f"===== WYNIK: {ok_iters}/{N} PASS =====")
        _handle_probe()
        _log("===== WALIDUJ_PETLA KONIEC =====")
    except Exception as err:
        _log(f"[BLAD TOP] {type(err).__name__}: {err}")
