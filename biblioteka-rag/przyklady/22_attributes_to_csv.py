# Wzorzec 22 (★ RDZEŃ workhorse, Faza A) — Eksport/import atrybutów bloków ↔ CSV.
#
# Kierunek zatwierdzony (research/05-decyzje.md): rank #3 (23/25). GstarCAD ma
# AutoXLSTable, ale nasza wartość to: (a) eksport WSZYSTKICH atrybutów do CSV do
# edycji w Excelu i re-import z powrotem (round-trip), (b) batch przez wiele plików,
# (c) reguły opisane po ludzku (LLM). To fundament „title block fill" i zestawień.
#
# STATUS: 🟡 DRAFT do walidacji na LC (razem ze sweep-10-text.py — API atrybutów/tekstu).
#         2026-07-10: API handle/nazwy-bloku/tekstu sprawdzone ze stubami pygrx.pyi
#         (getIntoAsciiBuffer, blockTableRecord+getName, textString) — runtime dalej pending LC.
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
        it.step()
    ms.close()
    for oid in ids:
        s, ref = gcdbOpenObject(oid, mode)
        if s == Gcad.eOk and ref is not None:
            h = "?"
            try:
                # handle = trwały identyfikator hex; w stubach: getIntoAsciiBuffer()->(bool,str).
                ok, hex_id = ref.handle().getIntoAsciiBuffer()
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
