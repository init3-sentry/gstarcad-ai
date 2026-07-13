# Wzorzec 23 (★ RDZEŃ workhorse, Faza A) — Renumeracja atrybutów wg reguły.
#
# Kierunek zatwierdzony (research/05-decyzje.md): rank #5 (22/25). GstarCAD ma
# Attribute Increment, ale tylko proste +1. Nasza wartość: reguła opisana po ludzku
# (prefiks + start + krok + format), np. pozycje „P-001, P-002...", rewizje, RFI.
# LLM w ASKAI generuje regułę z opisu klienta; ten wzorzec to referencyjny szkielet.
#
# STATUS: 🔴 ZAPIS ZABLOKOWANY. Renumeracja pisze setTextString na atrybucie, a to wywala
#         GstarCAD 2027 SP1 na regenie (empiria LC 13.07, 9 wariantow — patrz memory
#         feedback_gstarcad_attribute_write_bug). RENUMERUJ "Zrenumerowano 7" ale po ~10 min
#         idle GstarCAD padl. Do przepisania na DXF entMod. Odczyt (tag/wartosc) = OK.
#         NIE wysylac do chlopakow/Roberta poki nie przejdzie realnego testu na DXF.
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
            ent.close()
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
            # WZORZEC ZAPISU ATRYBUTOW (empiria LC 2026-07-13, 7 wariantow TESTCRASH):
            #  - blok kForWrite -> crash; atrybut standalone gcdbOpenObject -> crash;
            #  - JEDYNA dobra sciezka: blok kForRead + openAttribute(kForWrite) przez blok,
            #    ale iterator MUSI byc skonczony PRZED modyfikacja, a bloku NIE WOLNO zamykac
            #    (ref.close() po modyfikacji = crash; runtime sprzata na koncu komendy).
            s, obj = gcdbOpenObject(oid, GcDb.kForRead)
            if s != Gcad.eOk or obj is None:
                continue
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close()
                continue
            # 1) zbierz ID atrybutow (dokoncz iterator PRZED modyfikacja)
            aids = []
            try:
                it = ref.attributeIterator()
                while not it.done():
                    aids.append(it.objectId())
                    it.step()
            except Exception:
                pass
            if not aids:
                obj.close()   # blok bez atrybutow -> nietkniety -> mozna zamknac
                continue
            # 2) modyfikuj przez ten sam (read) blok; bloku NIE zamykamy
            for aid in aids:
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
            # NIE: ref.close() — read-blok ze zmodyfikowanymi atrybutami; close = crash.

        gcutPrintf(f"\nZrenumerowano {count} atrybutow '{tag}' (od {prefix}{str(start).zfill(pad)}, krok {step}).")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy renumeracji: {err}")
