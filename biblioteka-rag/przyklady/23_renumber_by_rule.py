# Wzorzec 23 (★ RDZEŃ workhorse, Faza A) — Renumeracja atrybutów wg reguły.
#
# Kierunek (research/05-decyzje.md): rank #5 (22/25). GstarCAD ma Attribute Increment,
# ale tylko proste +1. Nasza wartość: reguła opisana po ludzku (prefiks + start + krok).
#
# STATUS: 🟢 ZAPIS PRZEZ DXF (obejście buga GS 2027 SP1). Obiektowe setTextString na
#         atrybucie wywala GstarCAD na regenie (memory feedback_gstarcad_attribute_write_bug,
#         9 wariantów). OBEJŚCIE zwalidowane na LC 2026-07-13: zapis WYŁĄCZNIE przez ADS/DXF —
#         handEnt(INSERT) -> entNext -> ATTRIB -> entGet -> zmiana grupy 1 -> entMod -> entUpd.
#         KRYTYCZNE: ZERO attributeIterator/gcdbOpenObject na atrybutach (zatruwa entGet -> crash).
#         Potwierdzone: wartość zmieniona, entMod/entUpd=RTNORM, REGEN przeżył.
#
# Sposób użycia: APPLOAD, RENUMERUJ. Pyta o tag, prefiks, numer startowy, krok.

from pygcad.core.runtime import *
from pygcad.pygrx import *


# ── DXF/ADS helpers (zapis atrybutów bez obiektowego API — patrz STATUS) ──────────────

def _insert_handles():
    """Handle wszystkich ref. bloków w model space. TYLKO getEntity+isA+handle —
    NIE wolno dotykać attributeIterator/gcdbOpenObject na atrybutach (zatruwa entGet)."""
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
    """Pierwszy węzeł resbuf o danym kodzie grupy DXF (albo None)."""
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
    """Iteruje WSZYSTKIE atrybuty rysunku przez DXF; dla każdego woła
    fn(tag, value, set_value) -> gdzie set_value(new) ustawia nową wartość (grupa 1).
    Jeśli fn użyje set_value, zmiana jest zapisywana (entMod+entUpd). Zwraca liczbę zapisów."""
    written = 0
    for ih in _insert_handles():
        en = gds_name()
        if gcdbHandEnt(ih, en) != RTNORM:
            continue
        rb = gcdbEntGet(en)
        has_attr = _grp(rb, 66) is not None   # 66=1 -> atrybuty follow
        _free(rb)
        if not has_attr:
            continue
        cur = en
        for _ in range(500):  # bezpiecznik na wypadek braku SEQEND
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


# ── Komenda ───────────────────────────────────────────────────────────────────────────

@command(local_name='RENUMERUJ')
def renumberByRule():
    """Nadaje kolejne numery (prefiks+start+krok) atrybutom o wskazanym tagu — zapis przez DXF."""
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

        pad = 3
        state = {"cur": start, "count": 0}

        def rule(atag, aval, set_value):
            if atag == tag:
                set_value(f"{prefix}{str(state['cur']).zfill(pad)}")
                state["cur"] += step
                state["count"] += 1

        written = for_each_attribute(rule)
        gcutPrintf(f"\nZrenumerowano {written} atrybutow '{tag}' (od {prefix}{str(start).zfill(pad)}, krok {step}).")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy renumeracji: {err}")
