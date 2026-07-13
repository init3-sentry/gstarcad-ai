# SONDA IZOLACJI CRASHA PRZY ZAPISIE (MODYFIKUJE atrybuty — URUCHAMIAJ NA KOPII!).
# Cel 2026-07-13: IMPORT wywala GstarCAD przy wielu zapisach. TESTZAPIS: 1 zapis OK.
# Ta sonda zapisuje atrybuty PO KOLEI z licznikiem PRZED/PO kazdym zapisie.
# - jesli padnie na "W#k PRZED" -> winny konkretny k-ty zapis (jakis atrybut),
# - jesli wypisze wszystkie "PO" i padnie po petli -> to sprzatanie po N zapisach.
# Dodatkowo pyta o tryb otwarcia BLOKU (R/W) — sprawdzamy czy read-ref+write-attr rozni sie.
#
# Uzycie: APPLOAD, otworz KOPIE 30993, TESTCRASH, wpisz R (albo W). Skopiuj konsole.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _block_ref_ids():
    db = gcdbWorkingDatabase()
    ids = []
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return ids
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if s != Gcad.eOk:
        return ids
    s, it = ms.newIterator(); it.start()
    while not it.done():
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                if "BlockReference" in ent.isA().name():
                    ids.append(ent.objectId())
            except Exception:
                pass
            ent.close()
        it.step()
    ms.close()
    return ids


@command(local_name='TESTCRASH')
def testCrash():
    try:
        gcedInitGet(0, "R W")
        status, mode_kw = gcedGetKword("\nTryb otwarcia BLOKU [R/W] <R>: ")
        block_mode = GcDb.kForWrite if (status == RTNORM and mode_kw == "W") else GcDb.kForRead
        gcutPrintf(f"\nBLOK otwierany: {'kForWrite' if block_mode==GcDb.kForWrite else 'kForRead'}")

        n = 0
        for roid in _block_ref_ids():
            sr, obj = gcdbOpenObject(roid, block_mode)
            if sr != Gcad.eOk or obj is None:
                continue
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close(); continue
            try:
                ait = ref.attributeIterator()
                while not ait.done():
                    aid = ait.objectId()
                    sa, attr = ref.openAttribute(aid, GcDb.kForWrite)
                    if sa == Gcad.eOk and attr is not None:
                        n += 1
                        tag = ""
                        try: tag = attr.tag()
                        except Exception: pass
                        gcutPrintf(f"\nW#{n} PRZED  tag={tag}")
                        try:
                            attr.setTextString(f"T{n}")
                        except Exception as e:
                            gcutPrintf(f"  setTextString WYJATEK: {e}")
                        gcutPrintf(f"\nW#{n} PO")
                        attr.close()
                    ait.step()
            except Exception as e:
                gcutPrintf(f"\n  blad petli atrybutow: {e}")
            ref.close()
        gcutPrintf(f"\n=== PETLA OK: {n} zapisow zakonczonych (jesli crash TERAZ = sprzatanie po N) ===")
    except Exception as err:
        gcutPrintf(f"\n[BLAD TESTCRASH] {err}")
