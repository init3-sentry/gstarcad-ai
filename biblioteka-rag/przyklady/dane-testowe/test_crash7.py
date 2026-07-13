# SONDA v7 — v5 BEZ ref.close() na zmodyfikowanym bloku (crash byl DOKLADNIE tam).
# MODYFIKUJE atrybuty — URUCHOM i NIE ZAPISUJ (wpisuje smieci T1,T2...).
#
# Empiria 2026-07-13 (log -> C:\Users\Public\gs-ai\testcrash_log.txt):
#  v5: blok kForRead + zapis przez blok = 3 zapisy OK, crash na ref.close() tego bloku.
#  v6: atrybut standalone gcdbOpenObject(kForWrite) = crash na W#1 (martwe).
#  v4: blok kForWrite = crash na W#1.
#  => jedyna dzialajaca sciezka zapisu: blok kForRead + openAttribute(kForWrite) przez blok.
#     Jedyny crash: zamykanie tego bloku. v7 pomija close (runtime sprzata na koncu komendy).
#
# Wynik do interpretacji:
#  - "PETLA OK: 47" i BRAK crasha        -> FIX: modyfikuj przez read-blok, NIE zamykaj go.
#  - "PETLA OK: 47" a crash PO nim       -> zapisy OK, tylko odroczone zamkniecie pada (inny commit).
#  - crash w trakcie                     -> read-blok tez nie jest bezpieczny; zmieniam mechanizm (DXF).
#
# Uzycie: APPLOAD, 30993, TESTCRASH7.

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


@command(local_name='TESTCRASH7')
def testCrash7():
    fp = open(LOG, "w", encoding="utf-8")
    try:
        _log(fp, "START v7 read-blok BEZ close")
        gcutPrintf(f"\nLoguje do: {LOG}")
        n = 0
        b = 0
        for roid in _block_ref_ids():
            b += 1
            s, obj = gcdbOpenObject(roid, GcDb.kForRead)
            if s != Gcad.eOk or obj is None:
                continue
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close(); continue   # blok bez atrybutow — mozna zamknac (nietkniety)
            aids = []
            try:
                ait = ref.attributeIterator()
                while not ait.done():
                    aids.append(ait.objectId())
                    ait.step()
            except Exception as e:
                _log(fp, f"BLOK#{b} blad iteratora {e}")
            if not aids:
                obj.close()             # brak atrybutow -> blok nietkniety -> zamknij
                continue
            _log(fp, f"BLOK#{b}: {len(aids)} atrybutow, modyfikuje (NIE zamykam)")
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
            # UWAGA: celowo NIE wywolujemy ref.close() / obj.close() tutaj.
            _log(fp, f"BLOK#{b} zmodyfikowany, pominieto close")
        _log(fp, f"PETLA OK: {n} zapisow w {b} blokach")
        gcutPrintf(f"\n=== PETLA OK: {n} zapisow BEZ crasha (fix dziala!) ===")
    except Exception as err:
        _log(fp, f"WYJATEK GLOWNY {err}")
        gcutPrintf(f"\n[BLAD TESTCRASH7] {err}")
    finally:
        fp.close()
