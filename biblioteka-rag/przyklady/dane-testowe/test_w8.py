# SONDA v8 — blok kForWrite z POPRAWNYM zamknieciem (podrecznikowy commit atrybutow).
# MODYFIKUJE atrybuty — URUCHOM i NIE ZAPISUJ (wpisuje smieci T1,T2...).
#
# Empiria 2026-07-13 (log -> C:\Users\Public\gs-ai\testcrash_log.txt):
#  v5 blok kForRead + close  -> crash NATYCHMIAST na ref.close().
#  v7 blok kForRead BEZ close -> zapisy OK, ale crash ODROCZONY (idle po ~10 min).
#  v4 blok kForWrite          -> crash na W#1, ALE mial zatrucie globalnym pre-collectem.
#
# v8 = czysto (bez pre-collectu): blok kForWrite, dokoncz iterator, modyfikuj atrybuty,
#      zamknij atrybuty, ZAMKNIJ blok (kForWrite -> poprawny commit+regen). Jesli to
#      wariant stabilny, nie bedzie ani crasha teraz, ani po REGEN.
#
# Uzycie: APPLOAD, 30993, TESTW8. Po "PETLA OK" wpisz REGEN i poczekaj chwile.

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join("C:\\", "Users", "Public", "gs-ai", "testcrash_log.txt")


def _log(fp, msg):
    fp.write(msg + "\n")
    fp.flush()
    try:
        os.fsync(fp.fileno())
    except Exception:
        pass


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


@command(local_name='TESTW8')
def testW8():
    fp = open(LOG, "w", encoding="utf-8")
    try:
        _log(fp, "START v8 blok-kForWrite czysto")
        gcutPrintf(f"\nLoguje do: {LOG}")
        n = 0
        b = 0
        for roid in _block_ref_ids():
            b += 1
            s, obj = gcdbOpenObject(roid, GcDb.kForWrite)   # BLOK do ZAPISU
            if s != Gcad.eOk or obj is None:
                continue
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close(); continue
            aids = []
            try:
                ait = ref.attributeIterator()
                while not ait.done():
                    aids.append(ait.objectId())
                    ait.step()
            except Exception as e:
                _log(fp, f"BLOK#{b} blad iteratora {e}")
            if not aids:
                obj.close(); continue
            _log(fp, f"BLOK#{b}: {len(aids)} atrybutow")
            for aid in aids:
                n += 1
                _log(fp, f"W#{n} PRZED")
                sa, attr = ref.openAttribute(aid, GcDb.kForWrite)
                if sa == Gcad.eOk and attr is not None:
                    try:
                        attr.setTextString(f"T{n}")
                    except Exception as e:
                        _log(fp, f"W#{n} setTextString WYJATEK {e}")
                    attr.close()
                else:
                    _log(fp, f"W#{n} openAttribute status={sa}")
                _log(fp, f"W#{n} PO")
            obj.close()   # ZAMKNIJ blok kForWrite -> poprawny commit
            _log(fp, f"BLOK#{b} ZAMKNIETY")
        _log(fp, f"PETLA OK: {n} zapisow w {b} blokach")
        gcutPrintf(f"\n=== PETLA OK: {n} zapisow. Teraz wpisz REGEN i poczekaj. ===")
    except Exception as err:
        _log(fp, f"WYJATEK GLOWNY {err}")
        gcutPrintf(f"\n[BLAD TESTW8] {err}")
    finally:
        fp.close()
