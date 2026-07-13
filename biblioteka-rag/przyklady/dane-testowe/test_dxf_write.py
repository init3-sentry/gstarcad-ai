# SONDA DXF #6 — ZAPIS atrybutu przez entMod (obejscie BUG-01). MODYFIKUJE — NIE ZAPISUJ.
# Empiria: odczyt DXF atrybutu przez entNext dziala (grupa 1 = wartosc). Teraz zapis:
#   INSERT -> entNext -> ATTRIB -> entGet -> zmien wezel grupy 1 (rstring) -> gcdbEntMod
#   -> gcdbEntUpd(ename). ZERO obiektowego API atrybutow (attributeIterator zatruwa).
# Log PRZED/PO wokol entMod/entUpd + po REGEN. -> C:\Users\Public\gs-ai\dxf_log.txt
#
# Sukces = entMod/entUpd OK, wartosc zmieniona, BEZ crasha (takze po REGEN).
# Uzycie: RESTART GstarCAD, 30993, APPLOAD, TESTDXFWRITE. Po wyniku wpisz REGEN.

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join("C:\\", "Users", "Public", "gs-ai", "dxf_log.txt")
NEWVAL = "DXF_OK"


def _log(fp, m):
    fp.write(m + "\n")
    fp.flush()
    try:
        os.fsync(fp.fileno())
    except Exception:
        pass


def _first_blockref_handle():
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return None
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if s != Gcad.eOk:
        return None
    s, it = ms.newIterator(); it.start()
    h = None
    while not it.done() and h is None:
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                if "BlockReference" in ent.isA().name():
                    ok, hx = ent.getGcDbHandle().getIntoAsciiBuffer()
                    if ok:
                        h = hx
            except Exception:
                pass
            ent.close()
        it.step()
    ms.close()
    return h


def _grp(rb, code):
    """Zwroc pierwszy wezel o danym kodzie (albo None)."""
    node = rb
    while node is not None:
        try:
            if node.restype == code:
                return node
        except Exception:
            pass
        node = node.rbnext
    return None


@command(local_name='TESTDXFWRITE')
def testDxfWrite():
    fp = open(LOG, "w", encoding="utf-8")
    try:
        bh = _first_blockref_handle()
        _log(fp, f"pierwszy_blok handle={bh}")
        if not bh:
            _log(fp, "BRAK bloku"); return
        en = gds_name()
        if gcdbHandEnt(bh, en) != RTNORM:
            _log(fp, "handEnt != RTNORM"); return

        # entNext az do pierwszego ATTRIB (max 10 krokow)
        cur = en
        attr_en = None
        for step in range(10):
            nxt = gds_name()
            if gcdbEntNext(cur, nxt) != RTNORM:
                _log(fp, f"entNext #{step} != RTNORM -> brak ATTRIB"); break
            rb = gcdbEntGet(nxt)
            t = _grp(rb, 0)
            typ = None
            try:
                typ = t.resval.rstring if t is not None else None
            except Exception:
                pass
            _log(fp, f"entNext #{step}: typ={typ}")
            if typ == "ATTRIB":
                attr_en = nxt
                break
            try:
                gcutRelRb(rb)
            except Exception:
                pass
            cur = nxt

        if attr_en is None:
            _log(fp, "nie znaleziono ATTRIB"); return

        # entGet atrybutu, pokaz tag(2) + wartosc(1), zmien wartosc
        rb = gcdbEntGet(attr_en)
        tagn = _grp(rb, 2)
        valn = _grp(rb, 1)
        old = None
        try:
            old = valn.resval.rstring if valn is not None else None
        except Exception:
            pass
        tagv = None
        try:
            tagv = tagn.resval.rstring if tagn is not None else None
        except Exception:
            pass
        _log(fp, f"ATTRIB tag={tagv!r} wartosc_stara={old!r}")
        if valn is None:
            _log(fp, "BRAK grupy 1"); return

        valn.resval.rstring = NEWVAL
        _log(fp, f"ustawiono grupa1 -> {NEWVAL!r}")
        _log(fp, "PRZED gcdbEntMod")
        st_mod = gcdbEntMod(rb)
        _log(fp, f"PO gcdbEntMod status={st_mod}")
        _log(fp, "PRZED gcdbEntUpd")
        st_upd = gcdbEntUpd(attr_en)
        _log(fp, f"PO gcdbEntUpd status={st_upd}")
        _log(fp, "=== ZAPIS OK (bez crasha) — teraz wpisz REGEN ===")
        gcutPrintf(f"\n=== DXF ZAPIS OK: entMod={st_mod} entUpd={st_upd}. Wpisz REGEN i sprawdz atrybut. ===")
    except Exception as e:
        _log(fp, f"WYJATEK GLOWNY {e}")
        gcutPrintf(f"\n[BLAD] {e}")
    finally:
        fp.close()
