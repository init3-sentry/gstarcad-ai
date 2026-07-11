# Diagnostyk: gdzie w rysunku sa bloki z atrybutami? Skanuje WSZYSTKIE przestrzenie
# (model + kazdy uklad/paper space), nie tylko model space. Odpowiada, czemu
# EKSPORT_ATRYBUTOW zwrocil 0 na realnym pliku: brak atrybutow czy zla przestrzen.
# UZYCIE: (rysunek otwarty) APPLOAD -> attr-diag.py -> ATTR_DIAG. Log: Pulpit\attr-diag.txt

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "attr-diag.txt")


def _log(m, t=False):
    try:
        with open(LOG, "w" if t else "a", encoding="utf-8") as f:
            f.write(m + "\r\n")
    except Exception:
        pass
    try:
        gcutPrintf("\n" + m)
    except Exception:
        pass


def _scan_space(db, const, label):
    """Bezpieczny skan JEDNEJ przestrzeni (model/paper) sprawdzonym wzorcem getAt."""
    try:
        s, bt = db.getBlockTable(GcDb.kForRead)
        if s != Gcad.eOk:
            _log(f"  {label}: brak BlockTable"); return (0, 0)
        s, ms = bt.getAt(const, GcDb.kForRead)
        bt.close()
        if s != Gcad.eOk or ms is None:
            _log(f"  {label}: brak przestrzeni"); return (0, 0)
        nblk = 0; nattr = 0; ntext = 0; tags = set()
        s, it = ms.newIterator()
        it.start()
        while not it.done():
            s, ent = it.getEntity()
            if s == Gcad.eOk and ent is not None:
                try:
                    cls = ent.isA().name()
                except Exception:
                    cls = ""
                if "Text" in cls and "Attribute" not in cls:
                    ntext += 1
                elif "BlockReference" in cls:
                    nblk += 1
                    try:
                        ait = ent.attributeIterator()
                        while not ait.done():
                            aid = ait.objectId()
                            sa, a = ent.openAttribute(aid, GcDb.kForRead)
                            if sa == Gcad.eOk and a is not None:
                                nattr += 1
                                try: tags.add(a.tag())
                                except Exception: pass
                                a.close()
                            ait.step()
                    except Exception:
                        pass
                ent.close()
            it.step()
        ms.close()
        _log(f"  {label}: bloki={nblk}, atrybuty={nattr}, teksty(DBText/MText)={ntext}, tagi={sorted(tags)[:20]}")
        return (nattr, ntext)
    except Exception as e:
        _log(f"  {label}: BLAD {type(e).__name__}: {e}")
        return (0, 0)


@command(local_name='ATTR_DIAG')
def attrDiag():
    try:
        _log("=== ATTR_DIAG (bezpieczny: model + paper) ===", True)
        db = gcdbWorkingDatabase()
        a1, t1 = _scan_space(db, GCDB_MODEL_SPACE, "MODEL")
        a2, t2 = _scan_space(db, GCDB_PAPER_SPACE, "PAPER")
        _log(f"== RAZEM atrybuty={a1+a2}, teksty={t1+t2} ==")
        _log("(atrybuty>0 => sa bloki z atrybutami; atrybuty=0 a teksty duzo => tabelka to TEKST, nie atrybuty)")
    except Exception as err:
        _log(f"[BLAD] {type(err).__name__}: {err}")
