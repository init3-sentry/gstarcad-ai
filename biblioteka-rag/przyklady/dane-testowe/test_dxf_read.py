# SONDA DXF #5 (READ-ONLY) — CZYSTA sciezka ADS, ZERO obiektowego API atrybutow.
# Empiria: entGet(BA) dzialal, gdy blok znaleziony samym getEntity (v2). Padal, gdy przed
# entGet dotknieto attributeIterator/gcdbOpenObject (v4). Wniosek: obiektowe API atrybutow
# zatruwa entGet. Wiec discovery TYLKO getEntity+handle+isA (bez open/cast/attriter),
# potem czysto ADS: handEnt -> entGet(INSERT) -> entNext w atrybuty -> entGet kazdy.
# Log PRZED/PO + gcutRelRb. URUCHOM PO RESTARCIE. Log -> C:\Users\Public\gs-ai\dxf_log.txt

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join("C:\\", "Users", "Public", "gs-ai", "dxf_log.txt")


def _log(fp, m):
    fp.write(m + "\n")
    fp.flush()
    try:
        os.fsync(fp.fileno())
    except Exception:
        pass


def _first_blockref_handle():
    """handle pierwszej ref. bloku — TYLKO getEntity+isA+handle (bez open/cast/attriter)."""
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


def _chain_info(rb):
    node = rb
    i = 0
    info = []
    while node is not None and i < 60:
        try:
            rt = node.restype
        except Exception:
            rt = "?"
        if isinstance(rt, int) and rt in (0, 1, 2, 8, 66):
            v = "?"
            if rt == 66:
                try:
                    v = str(node.resval.rint)
                except Exception:
                    v = "?"
            else:
                try:
                    v = repr(node.resval.rstring)
                except Exception:
                    v = "?"
            info.append(f"{rt}={v}")
        node = node.rbnext
        i += 1
    return " | ".join(info), i


def _free(rb):
    try:
        gcutRelRb(rb)
    except Exception:
        pass


@command(local_name='TESTDXFREAD')
def testDxfRead():
    fp = open(LOG, "w", encoding="utf-8")
    try:
        bh = _first_blockref_handle()
        _log(fp, f"pierwszy_blok handle={bh}")
        if not bh:
            _log(fp, "BRAK bloku")
            return
        en = gds_name()
        st = gcdbHandEnt(bh, en)
        _log(fp, f"handEnt(INSERT)={st}")
        if st != RTNORM:
            return
        _log(fp, "PRZED entGet(INSERT)")
        rb = gcdbEntGet(en)
        _log(fp, f"PO entGet(INSERT) None?{rb is None}")
        desc, n = _chain_info(rb)
        _log(fp, f"INSERT: {desc}  ({n})")
        _free(rb)

        cur = en
        for step in range(8):
            nxt = gds_name()
            _log(fp, f"PRZED entNext #{step}")
            st = gcdbEntNext(cur, nxt)
            _log(fp, f"entNext #{step}={st}")
            if st != RTNORM:
                _log(fp, "  koniec")
                break
            _log(fp, f"PRZED entGet #{step}")
            rb2 = gcdbEntGet(nxt)
            _log(fp, f"PO entGet #{step} None?{rb2 is None}")
            desc, n = _chain_info(rb2)
            _log(fp, f"  encja #{step}: {desc}  ({n})")
            _free(rb2)
            cur = nxt
        _log(fp, "=== KONIEC ===")
        gcutPrintf(f"\nTESTDXFREAD OK, log w {LOG}")
    except Exception as e:
        _log(fp, f"WYJATEK GLOWNY {e}")
        gcutPrintf(f"\n[BLAD] {e}")
    finally:
        fp.close()
