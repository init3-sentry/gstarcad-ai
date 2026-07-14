# Wzorzec 21 (★ RDZEŃ workhorse, Faza A) — Znajdź i zamień tekst.
#
# Kierunek (research/05-decyzje.md): rank #1 (24/25). GstarCAD ma natywne Find&Replace,
# ale tylko w jednym rysunku, bez reguł/batcha. Nasza wartość: batch + reguła LLM.
#
# STATUS: 🟢 CAŁOŚĆ PRZEZ DXF/ADS (obejście buga GS 2027 SP1). Obiektowe API zapisu
#         (setTextString) wywala GstarCAD na regenie; attributeIterator zatruwa entGet
#         (memory feedback_gstarcad_attribute_write_bug, 9 wariantów, LC 2026-07-13).
#         Dlatego zamiana idzie wyłącznie przez DXF:
#           - ATRYBUTY: handEnt(INSERT) -> entNext -> ATTRIB -> entGet -> grupa 1 -> entMod/entUpd.
#           - TEKSTY/MTEKSTY (top-level): handEnt -> entGet -> grupy 1 (+3 dla MText) -> entMod/entUpd.
#         Silnik DXF zwalidowany na LC (RENUMERUJ/EKSPORT na 30993, REGEN bez crasha).
#         Uwaga BUG-01b: justowane teksty po zmianie wartości mogą nie re-centrować się (kosmetyka).
#
# Sposób użycia: APPLOAD, ZAMIEN_TEKST. Pyta o szukany tekst i tekst docelowy; podmienia
# we WSZYSTKICH tekstach/mtekstach/atrybutach bieżącego rysunku.

# @KATALOG
# nazwa: Zamiana tekstów hurtem
# komenda: ZAMIEN_TEKST
# branza: ogólne
# opis: Znajdź-i-zamień naraz we wszystkich tekstach, mtekstach i atrybutach bloków całego rysunku. Zamiast poprawiać setki opisów ręcznie, zmieniasz np. nazwę inwestycji jednym poleceniem.
# przyklad: Zmiana numeru działki w 200 opisach na rzucie jednym ruchem.

from pygcad.core.runtime import *
from pygcad.pygrx import *


# ── DXF/ADS helpers (bez obiektowego API atrybutów) ─────────────────────────────────────

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


def _text_handles():
    """Handle top-level tekstów/mtekstów (nie atrybutów — te są sub-encjami INSERT-ów)."""
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
                cls = ent.isA().name()
                if "Text" in cls and "Attribute" not in cls:
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


def _for_each_attribute(fn):
    """fn(tag, value, set_value); set_value(new) zapisuje grupę 1. Zwraca liczbę zapisów."""
    written = 0
    for ih in _insert_handles():
        en = gds_name()
        if gcdbHandEnt(ih, en) != RTNORM:
            continue
        rb = gcdbEntGet(en)
        has_attr = _grp(rb, 66) is not None
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

                def set_value(new, _b=box):
                    _b["new"] = new

                fn(tag, val, set_value)
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


def _replace_in_text(handle, find, repl):
    """Podmiana w tekście/mtekście top-level przez DXF (grupy 1 i 3). Zwraca True gdy zmieniono."""
    en = gds_name()
    if gcdbHandEnt(handle, en) != RTNORM:
        return False
    rb = gcdbEntGet(en)
    changed = False
    node = rb
    while node is not None:
        try:
            if node.restype in (1, 3):
                s = node.resval.rstring
                if isinstance(s, str) and find in s:
                    node.resval.rstring = s.replace(find, repl)
                    changed = True
        except Exception:
            pass
        node = node.rbnext
    if changed:
        try:
            if gcdbEntMod(rb) == RTNORM:
                gcdbEntUpd(en)
            else:
                changed = False
        except Exception:
            changed = False
    _free(rb)
    return changed


# ── Komenda ─────────────────────────────────────────────────────────────────────────────

@command(local_name='ZAMIEN_TEKST')
def batchFindReplace():
    """Znajdź i zamień tekst we wszystkich tekstach/mtekstach/atrybutach — zapis przez DXF."""
    try:
        status, find = gcedGetString(1, "\nSzukany tekst: ")   # 1 = zezwól na spacje
        if status != RTNORM or not find:
            gcutPrintf("\nAnulowano.")
            return
        status, repl = gcedGetString(1, "\nZamień na: ")
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # 1) atrybuty bloków (DXF)
        def rule(tag, val, set_value):
            if val and find in val:
                set_value(val.replace(find, repl))

        n_attr = _for_each_attribute(rule)

        # 2) teksty i mteksty top-level (DXF)
        n_text = 0
        for h in _text_handles():
            if _replace_in_text(h, find, repl):
                n_text += 1

        gcutPrintf(f"\nZamieniono '{find}' -> '{repl}' w {n_attr + n_text} miejscach "
                   f"(teksty: {n_text}, atrybuty: {n_attr}).")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy zamianie: {err}")
