# Wzorzec 22 (★ RDZEŃ workhorse, Faza A) — Eksport/import atrybutów bloków ↔ CSV.
#
# Kierunek (research/05-decyzje.md): rank #3 (23/25). Wartość: (a) eksport WSZYSTKICH
# atrybutów do CSV do edycji w Excelu i re-import (round-trip), (b) batch, (c) reguły LLM.
#
# STATUS: 🟢 CAŁOŚĆ PRZEZ DXF/ADS (obejście buga GS 2027 SP1). Obiektowe API atrybutów
#         (attributeIterator/openAttribute/setTextString) wywala GstarCAD: zapis na regenie,
#         a samo dotknięcie attributeIterator zatruwa późniejszy entGet -> crash (memory
#         feedback_gstarcad_attribute_write_bug, 9 wariantów, LC 2026-07-13). Dlatego ZARÓWNO
#         eksport (odczyt) JAK i import (zapis) idą wyłącznie przez DXF: handEnt(INSERT) ->
#         entNext -> ATTRIB -> entGet (grupa 1=wartość, 2=tag) -> [entMod+entUpd przy zapisie].
#         Handle bloku = getGcDbHandle (==DXF grupa 5 INSERT-a). Zwalidowane: RENUMERUJ na
#         tym samym silniku DXF -> zapis + REGEN bez crasha na 30993.
#
# Sposób użycia: APPLOAD, następnie:
#   EKSPORT_ATRYBUTOW — wszystkie atrybuty -> CSV na Pulpicie (handle,blok,tag,wartość).
#   IMPORT_ATRYBUTOW  — czyta CSV i aktualizuje wartości (dopasowanie handle+tag).

# @KATALOG
# nazwa: Eksport atrybutów do tabeli
# komenda: EKSPORT_ATRYBUTOW
# branza: ogólne
# opis: Wyciąga wszystkie atrybuty bloków rysunku (z tabelek, stempli, metryk) do pliku CSV do edycji w Excelu. Fundament pod zestawienia i masową edycję danych.
# przyklad: Wyeksportowanie metryk wszystkich pomieszczeń do arkusza.
# @KATALOG
# nazwa: Import atrybutów z tabeli
# komenda: IMPORT_ATRYBUTOW
# branza: ogólne
# opis: Wczytuje z powrotem do rysunku wartości atrybutów po edycji w Excelu (dopasowanie po handle i tagu). Domyka round-trip: eksport, poprawki hurtem, import.
# przyklad: Aktualizacja powierzchni w 50 metrykach po przeliczeniu w arkuszu.

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
import csv

CSV_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "atrybuty_gstarcad.csv")


# ── DXF/ADS helpers (bez obiektowego API atrybutów — patrz STATUS) ──────────────────────

def _insert_handles():
    """Handle ref. bloków w model space. TYLKO getEntity+isA+handle (bez attributeIterator)."""
    db = gcdbWorkingDatabase()
    out = []
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return out
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if s != Gcad.eOk:
        return out
    s, it = ms.newIterator(); it.start()
    while not it.done():
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                if "BlockReference" in ent.isA().name():
                    ok, hx = ent.getGcDbHandle().getIntoAsciiBuffer()
                    if ok:
                        out.append(hx)
            except Exception:
                pass
            ent.close()
        it.step()
    ms.close()
    return out


def _grp(rb, code):
    node = rb
    while node is not None:
        try:
            if node.restype == code:
                return node
        except Exception:
            pass
        node = node.rbnext
    return None


def _rstr(node):
    try:
        return node.resval.rstring if node is not None else None
    except Exception:
        return None


def _free(rb):
    try:
        gcutRelRb(rb)
    except Exception:
        pass


def for_each_attribute(fn):
    """Dla każdego atrybutu rysunku (przez DXF) woła fn(insert_handle, block_name, tag,
    value, set_value). set_value(new) ustawia nową wartość (grupa 1) i zapisuje entMod+entUpd.
    Zwraca liczbę zapisów."""
    written = 0
    for ih in _insert_handles():
        en = gds_name()
        if gcdbHandEnt(ih, en) != RTNORM:
            continue
        rb = gcdbEntGet(en)
        has_attr = _grp(rb, 66) is not None
        bname = _rstr(_grp(rb, 2)) or "?"   # INSERT grupa 2 = nazwa bloku
        _free(rb)
        if not has_attr:
            continue
        cur = en
        for _ in range(500):
            nxt = gds_name()
            if gcdbEntNext(cur, nxt) != RTNORM:
                break
            rb = gcdbEntGet(nxt)
            typ = _rstr(_grp(rb, 0))
            if typ == "SEQEND":
                _free(rb)
                break
            if typ == "ATTRIB":
                tag = _rstr(_grp(rb, 2))
                valn = _grp(rb, 1)
                val = _rstr(valn)
                box = {"new": None}

                def set_value(new, _box=box):
                    _box["new"] = new

                fn(ih, bname, tag, val, set_value)
                if box["new"] is not None and valn is not None:
                    try:
                        valn.resval.rstring = box["new"]
                        if gcdbEntMod(rb) == RTNORM:
                            gcdbEntUpd(nxt)
                            written += 1
                    except Exception:
                        pass
            _free(rb)
            cur = nxt
    return written


# ── Komendy ─────────────────────────────────────────────────────────────────────────────

@command(local_name='EKSPORT_ATRYBUTOW')
def exportAttributes():
    """Zapisuje wszystkie atrybuty bloków bieżącego rysunku do CSV na Pulpicie."""
    try:
        rows = []

        def collect(ih, bname, tag, val, set_value):
            rows.append([ih, bname, tag or "", val or ""])

        for_each_attribute(collect)
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

        def apply(ih, bname, tag, val, set_value):
            key = (ih, tag or "")
            if key in wanted and (val or "") != wanted[key]:
                set_value(wanted[key])

        updated = for_each_attribute(apply)
        gcutPrintf(f"\nZaktualizowano {updated} atrybutów z CSV.")
    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy imporcie atrybutów: {err}")
