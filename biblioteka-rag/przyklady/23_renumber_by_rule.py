# Wzorzec 23 (★ RDZEŃ workhorse, Faza A) — Renumeracja atrybutów wg reguły.
#
# Kierunek zatwierdzony (research/05-decyzje.md): rank #5 (22/25). GstarCAD ma
# Attribute Increment, ale tylko proste +1. Nasza wartość: reguła opisana po ludzku
# (prefiks + start + krok + format), np. pozycje „P-001, P-002...", rewizje, RFI.
# LLM w ASKAI generuje regułę z opisu klienta; ten wzorzec to referencyjny szkielet.
#
# STATUS: 🟡 DRAFT do walidacji na LC (razem ze sweep-10-text.py — API atrybutów).
#
# Sposób użycia: APPLOAD, następnie RENUMERUJ. Komenda pyta o: tag atrybutu do
# renumeracji (np. NUMER), prefiks (np. „P-"), numer startowy, krok. Następnie
# nadaje kolejne wartości wszystkim atrybutom o tym tagu w kolejności napotkania.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _set_str(ent, s):
    for setter in ("setTextString", "setContents"):
        try:
            fn = getattr(ent, setter, None)
            if fn is None:
                continue
            fn(s)
            return True
        except Exception:
            continue
    return False


def _block_ref_ids():
    """ObjectId wszystkich referencji bloków w model space."""
    db = gcdbWorkingDatabase()
    ids = []
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return ids
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if s != Gcad.eOk:
        return ids
    s, it = ms.newIterator()
    it.start()
    while not it.done():
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                if "BlockReference" in ent.isA().name():
                    ids.append(ent.objectId())
            except Exception:
                pass
        it.step()
    ms.close()
    return ids


@command(local_name='RENUMERUJ')
def renumberByRule():
    """Nadaje kolejne numery (prefiks+start+krok) atrybutom o wskazanym tagu."""
    try:
        status, tag = gcedGetString(0, "\nTag atrybutu do renumeracji (np. NUMER): ")
        if status != RTNORM or not tag:
            gcutPrintf("\nAnulowano.")
            return
        status, prefix = gcedGetString(1, "\nPrefiks (np. P-, Enter = brak): ")
        if status != RTNORM:
            prefix = ""
        status, start = gcedGetInt("\nNumer startowy: ")
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        status, step = gcedGetInt("\nKrok: ")
        if status != RTNORM or step == 0:
            step = 1

        # szerokość zer wiodących wg największego spodziewanego numeru (proste: 3 cyfry)
        pad = 3
        current = start
        count = 0

        for oid in _block_ref_ids():
            s, ref = gcdbOpenObject(oid, GcDb.kForWrite)
            if s != Gcad.eOk or ref is None:
                continue
            try:
                it = ref.attributeIterator()
                while not it.done():
                    aid = it.objectId()
                    sa, attr = ref.openAttribute(aid, GcDb.kForWrite)
                    if sa == Gcad.eOk and attr is not None:
                        atag = ""
                        try:
                            atag = attr.tag()
                        except Exception:
                            pass
                        if atag == tag:
                            newval = f"{prefix}{str(current).zfill(pad)}"
                            if _set_str(attr, newval):
                                current += step
                                count += 1
                        attr.close()
                    it.step()
            except Exception:
                pass
            ref.close()

        gcutPrintf(f"\nZrenumerowano {count} atrybutów „{tag}" (od {prefix}{str(start).zfill(pad)}, krok {step}).")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy renumeracji: {err}")
