# SONDA DIAGNOSTYCZNA (read-only, BEZPIECZNA — nic nie zapisuje).
# Cel 2026-07-13: rozstrzygnac empirycznie, ktora metoda odczytu tekstu dziala
# i czy dziala w trybie kForRead (podejrzenie regresu ZAMIEN 3->0).
#
# Uzycie: APPLOAD, potem TESTREAD na dowolnym rysunku z tekstami/atrybutami (np. 30588/30993).
# Skopiuj CALA konsole do raportu.

from pygcad.core.runtime import *
from pygcad.pygrx import *

GETTERS = ("textString", "textStringConst", "contents", "text")


def _dump(ent, label):
    """Wypisz wynik kazdego gettera dla encji (juz otwartej + zcastowanej)."""
    for g in GETTERS:
        try:
            fn = getattr(ent, g, None)
            if fn is None:
                gcutPrintf(f"\n    {label} {g}: BRAK METODY")
                continue
            val = fn()
            gcutPrintf(f"\n    {label} {g}: {type(val).__name__} = {repr(val)[:60]}")
        except Exception as e:
            gcutPrintf(f"\n    {label} {g}: WYJATEK {e}")


@command(local_name='TESTREAD')
def testRead():
    try:
        db = gcdbWorkingDatabase()
        s, bt = db.getBlockTable(GcDb.kForRead)
        s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        text_ids, ref_ids = [], []
        s, it = ms.newIterator(); it.start()
        while not it.done():
            s, ent = it.getEntity()
            if s == Gcad.eOk and ent is not None:
                try:
                    cls = ent.isA().name()
                    if "Text" in cls and "Attribute" not in cls:
                        text_ids.append((ent.objectId(), cls))
                    elif "BlockReference" in cls:
                        ref_ids.append(ent.objectId())
                except Exception:
                    pass
                ent.close()
            it.step()
        ms.close()

        gcutPrintf(f"\n=== TESTREAD: {len(text_ids)} tekstow, {len(ref_ids)} blokow ===")

        # A) TEKSTY: odczyt w kForRead vs kForWrite (do 3)
        for oid, cls in text_ids[:3]:
            gcutPrintf(f"\n[TEKST {cls}]")
            for mode, mname in ((GcDb.kForRead, "READ"), (GcDb.kForWrite, "WRITE")):
                sr, ent = gcdbOpenObject(oid, mode)
                if sr == Gcad.eOk and ent is not None:
                    t = GcDbMText.cast(ent) if "MText" in cls else GcDbText.cast(ent)
                    gcutPrintf(f"\n  tryb={mname} cast={'OK' if t is not None else 'None'}")
                    if t is not None:
                        _dump(t, mname)
                    ent.close()

        # B) ATRYBUTY: pierwszy blok z atrybutami, do 5 atrybutow (kForRead)
        shown = 0
        for roid in ref_ids:
            sr, obj = gcdbOpenObject(roid, GcDb.kForRead)
            if sr != Gcad.eOk or obj is None:
                continue
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close(); continue
            try:
                ait = ref.attributeIterator()
                while not ait.done() and shown < 5:
                    sa, attr = ref.openAttribute(ait.objectId(), GcDb.kForRead)
                    if sa == Gcad.eOk and attr is not None:
                        tag = ""
                        try: tag = attr.tag()
                        except Exception: pass
                        gcutPrintf(f"\n[ATRYBUT tag={tag}]")
                        _dump(attr, "READ")
                        attr.close(); shown += 1
                    ait.step()
            except Exception as e:
                gcutPrintf(f"\n  blad atrybutow: {e}")
            ref.close()
            if shown >= 5:
                break
        gcutPrintf("\n=== KONIEC TESTREAD ===")
    except Exception as err:
        gcutPrintf(f"\n[BLAD TESTREAD] {err}")
