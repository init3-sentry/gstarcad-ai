# SONDA v9 — v5 + adjustAlignment(db) po setTextString (BRAKUJACY klocek ObjectARX).
# MODYFIKUJE atrybuty — URUCHOM i NIE ZAPISUJ (wpisuje smieci T1,T2...).
#
# Empiria 2026-07-13: zapis atrybutu ZAWSZE sie udaje, ale close bloku (v5 kForRead / v8
# kForWrite) = crash natychmiast, brak close = crash odroczony (idle/REGEN). Wniosek:
# crash w REGENIE grafiki atrybutu. GcDbText.adjustAlignment(pDb) przelicza geometrie
# tekstu po zmianie stringa — bez tego grafika jest nieaktualna. NIE bylo wywolane.
#
# v9 = v5 (blok kForRead, zapis przez blok, potem ref.close()) + JEDNA linia
#      attr.adjustAlignment(db) po setTextString. Sukces = PETLA OK + przezyty REGEN.
#
# Uzycie: APPLOAD, 30993, TESTW9. Po "PETLA OK" wpisz REGEN i poczekaj ~20 s.

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


@command(local_name='TESTW9')
def testW9():
    fp = open(LOG, "w", encoding="utf-8")
    db = gcdbWorkingDatabase()
    try:
        _log(fp, "START v9 kForRead + adjustAlignment")
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
                    # KLUCZ: przelicz geometrie tekstu po zmianie stringa
                    try:
                        attr.adjustAlignment(db)
                    except Exception as e:
                        try:
                            attr.adjustAlignment()
                        except Exception as e2:
                            _log(fp, f"W#{n} adjustAlignment WYJATEK {e2}")
                    attr.close()
                else:
                    _log(fp, f"W#{n} openAttribute status={sa}")
                _log(fp, f"W#{n} PO")
            ref.close()   # zamykamy blok — z przeliczona grafika powinno przezyc
            _log(fp, f"BLOK#{b} ZAMKNIETY")
        _log(fp, f"PETLA OK: {n} zapisow w {b} blokach")
        gcutPrintf(f"\n=== PETLA OK: {n} zapisow. Teraz wpisz REGEN i poczekaj. ===")
    except Exception as err:
        _log(fp, f"WYJATEK GLOWNY {err}")
        gcutPrintf(f"\n[BLAD TESTW9] {err}")
    finally:
        fp.close()
