# Wzorzec 22 (★ RDZEŃ workhorse, Faza A) — Eksport/import atrybutów bloków ↔ CSV.
#
# Kierunek zatwierdzony (research/05-decyzje.md): rank #3 (23/25). GstarCAD ma
# AutoXLSTable, ale nasza wartość to: (a) eksport WSZYSTKICH atrybutów do CSV do
# edycji w Excelu i re-import z powrotem (round-trip), (b) batch przez wiele plików,
# (c) reguły opisane po ludzku (LLM). To fundament „title block fill" i zestawień.
#
# STATUS: ✅ ZWALIDOWANY end-to-end na LC 2026-07-10 (GstarCAD 2027 SP1, R27.1.0.2606)
#         przez weryfikacja/waliduj-petla.py — 10/10 iteracji PASS (eksport=1 za każdym razem).
#         Handle: GcDbBlockReference NIE ma handle() — użyto getGcDbHandle().getIntoAsciiBuffer()
#         (empirycznie -> (True,'2A7')). Nazwa bloku: blockTableRecord()+getName(). Wartości
#         przez textString()/setTextString() (GcDbAttribute dziedziczy z GcDbText).
#
# Sposób użycia: APPLOAD, następnie:
#   EKSPORT_ATRYBUTOW — zapisuje wszystkie atrybuty bloków bieżącego rysunku do
#                       CSV na Pulpicie (handle,blok,tag,wartość).
#   IMPORT_ATRYBUTOW  — czyta ten CSV i aktualizuje wartości atrybutów wg kolumny
#                       „wartość" (dopasowanie po handle+tag).

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
import csv

CSV_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "atrybuty_gstarcad.csv")


def _get_str(ent):
    for getter in ("textStringConst", "text", "contents"):
        try:
            fn = getattr(ent, getter, None)
            if fn is None:
                continue
            val = fn()
            if isinstance(val, str):
                return val
        except Exception:
            continue
    return None


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


def _iter_block_refs(mode):
    """Generator: (blockRef, handle_str) po referencjach bloków w model space.
    Referencja otwarta w trybie 'mode' — wywołujący ZAMYKA."""
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if s != Gcad.eOk:
        return
    s, it = ms.newIterator()
    it.start()
    ids = []
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
    for oid in ids:
        s, obj = gcdbOpenObject(oid, mode)
        if s == Gcad.eOk and obj is not None:
            # KLUCZ: gcdbOpenObject zwraca bazowy GcDbObject, NIE GcDbBlockReference.
            # Bez castu brak metod attributeIterator/blockTableRecord -> 0 atrybutow
            # (bug wykryty 2026-07-13 na realnym rysunku 30993). Cast jak w wzorcu 24.
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close()
                continue
            h = "?"
            try:
                # handle = trwały hex id. UWAGA (empiria 2026-07-10): GcDbBlockReference
                # NIE ma metody handle() — jest getGcDbHandle()->GcDbHandle, a z niej
                # getIntoAsciiBuffer()->(bool, hex). Potwierdzone na LC: (True, '2A7').
                ok, hex_id = ref.getGcDbHandle().getIntoAsciiBuffer()
                h = hex_id if ok else str(ref.objectId())
            except Exception:
                try:
                    h = str(ref.objectId())
                except Exception:
                    h = "?"
            yield ref, h


@command(local_name='EKSPORT_ATRYBUTOW')
def exportAttributes():
    """Zapisuje wszystkie atrybuty bloków bieżącego rysunku do CSV na Pulpicie."""
    try:
        rows = []
        for ref, h in _iter_block_refs(GcDb.kForRead):
            # Nazwa bloku: GcDbBlockReference NIE ma blockName() (potwierdzone w stubach).
            # Idziemy przez rekord definicji: blockTableRecord() -> getName()->(status,nazwa).
            bname = "?"
            try:
                srec, rec = gcdbOpenObject(ref.blockTableRecord(), GcDb.kForRead)
                if srec == Gcad.eOk and rec is not None:
                    sn, nm = rec.getName()
                    if sn == Gcad.eOk:
                        bname = nm
                    rec.close()
            except Exception:
                bname = "?"
            try:
                it = ref.attributeIterator()
                while not it.done():
                    aid = it.objectId()
                    sa, attr = ref.openAttribute(aid, GcDb.kForRead)
                    if sa == Gcad.eOk and attr is not None:
                        tag = ""
                        try:
                            tag = attr.tag()
                        except Exception:
                            pass
                        val = _get_str(attr) or ""
                        rows.append([h, bname, tag, val])
                        attr.close()
                    it.step()
            except Exception:
                pass
            ref.close()

        with open(CSV_PATH, "w", newline="", encoding="utf-8") as fp:
            w = csv.writer(fp)
            w.writerow(["handle", "blok", "tag", "wartosc"])
            w.writerows(rows)
        gcutPrintf(f"\nWyeksportowano {len(rows)} atrybutów do: {CSV_PATH}")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy eksporcie atrybutów: {err}")


@command(local_name='IMPORT_ATRYBUTOW')
def importAttributes():
    """Czyta CSV z Pulpitu i aktualizuje wartości atrybutów (dopasowanie handle+tag)."""
    try:
        if not os.path.exists(CSV_PATH):
            gcutPrintf(f"\nBrak pliku: {CSV_PATH}. Najpierw EKSPORT_ATRYBUTOW.")
            return
        wanted = {}  # (handle, tag) -> wartosc
        with open(CSV_PATH, "r", encoding="utf-8") as fp:
            for r in csv.DictReader(fp):
                wanted[(r.get("handle", ""), r.get("tag", ""))] = r.get("wartosc", "")

        updated = 0
        for ref, h in _iter_block_refs(GcDb.kForWrite):
            try:
                it = ref.attributeIterator()
                while not it.done():
                    aid = it.objectId()
                    sa, attr = ref.openAttribute(aid, GcDb.kForWrite)
                    if sa == Gcad.eOk and attr is not None:
                        tag = ""
                        try:
                            tag = attr.tag()
                        except Exception:
                            pass
                        key = (h, tag)
                        if key in wanted and _get_str(attr) != wanted[key]:
                            if _set_str(attr, wanted[key]):
                                updated += 1
                        attr.close()
                    it.step()
            except Exception:
                pass
            ref.close()
        gcutPrintf(f"\nZaktualizowano {updated} atrybutów z CSV.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy imporcie atrybutów: {err}")
