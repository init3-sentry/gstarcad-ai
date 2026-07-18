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
#   GSAI_EKSPORT_ATRYBUTOW (EN: GSAI_EXPORTATTR) — wszystkie atrybuty -> CSV na Pulpicie (handle,blok,tag,wartość).
#   GSAI_IMPORT_ATRYBUTOW  (EN: GSAI_IMPORTATTR) — czyta CSV i aktualizuje wartości (dopasowanie handle+tag).


from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
import csv
import io

CSV_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "atrybuty_gstarcad.csv")

# Kolejnosc prob odczytu. utf-8-sig zdejmuje znacznik BOM i czyta zwykle utf-8.
# cp1250 to domyslny zapis Excela w polskim Windows, gdy uzytkownik wybierze
# "CSV (rozdzielany przecinkami)" zamiast "CSV UTF-8".
_KODOWANIA = ("utf-8-sig", "cp1250", "cp852")


def _wczytaj_tekst(sciezka):
    """Czyta plik, probujac kolejnych kodowan. Zwraca None, gdy zadne nie pasuje."""
    for kod in _KODOWANIA:
        try:
            with open(sciezka, "r", encoding=kod, newline="") as fp:
                return fp.read()
        except UnicodeDecodeError:
            continue
    return None


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

@command(local_name='GSAI_EKSPORT_ATRYBUTOW', global_name='GSAI_EXPORTATTR', group_name='GSAI')
def exportAttributes():
    """Zapisuje wszystkie atrybuty bloków bieżącego rysunku do CSV na Pulpicie."""
    try:
        rows = []

        def collect(ih, bname, tag, val, set_value):
            rows.append([ih, bname, tag or "", val or ""])

        for_each_attribute(collect)
        # Sredniki i utf-8-sig, bo tego wymaga Excel w polskiej wersji.
        # Przecinek wrzuca caly wiersz do jednej kolumny, a brak znacznika
        # kodowania psuje polskie znaki. Robert Nowakowski zglosil oba objawy
        # w natywnym ATTIN (2026-07-18) — mielismy je tak samo.
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as fp:
            w = csv.writer(fp, delimiter=";")
            w.writerow(["handle", "blok", "tag", "wartosc"])
            w.writerows(rows)
        gcutPrintf(f"\nWyeksportowano {len(rows)} atrybutów do: {CSV_PATH}")
    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy eksporcie atrybutów: {err}")


@command(local_name='GSAI_IMPORT_ATRYBUTOW', global_name='GSAI_IMPORTATTR', group_name='GSAI')
def importAttributes():
    """Czyta CSV z Pulpitu i aktualizuje wartości atrybutów (dopasowanie handle+tag)."""
    try:
        if not os.path.exists(CSV_PATH):
            gcutPrintf(f"\nBrak pliku: {CSV_PATH}. Najpierw GSAI_EKSPORT_ATRYBUTOW.")
            return
        wanted = {}  # (handle, tag) -> wartosc
        tekst = _wczytaj_tekst(CSV_PATH)
        if tekst is None:
            gcutPrintf("\n[BLAD] Nie umiem odczytac pliku CSV — nieznane kodowanie.")
            return
        sep = ";" if tekst.count(";") >= tekst.count(",") else ","
        for r in csv.DictReader(io.StringIO(tekst), delimiter=sep):
            wanted[(r.get("handle", ""), r.get("tag", ""))] = r.get("wartosc", "")

        def apply(ih, bname, tag, val, set_value):
            key = (ih, tag or "")
            if key in wanted and (val or "") != wanted[key]:
                set_value(wanted[key])

        updated = for_each_attribute(apply)
        gcutPrintf(f"\nZaktualizowano {updated} atrybutów z CSV.")
    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy imporcie atrybutów: {err}")
