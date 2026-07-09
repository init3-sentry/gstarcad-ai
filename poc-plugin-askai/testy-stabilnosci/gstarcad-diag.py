# =====================================================================
# gstarcad-diag.py — uniwersalny skrypt diagnostyczny stabilności pygcad
# Projekt gstarcad-ai / TMSys. Wersja 1.0 (2026-07-10).
#
# CEL: sprawdzić na wielu maszynach lokalnych (NIE przez RDP), czy GstarCAD
# 2027 Premium SP1 jest stabilny na tym samym zestawie operacji pygcad, który
# na maszynie zdalnej (RDP) crashował. Rozstrzyga: czy crashe to produkt, czy
# środowisko RDP.
#
# WSZYSTKO loguje się do pliku (z natychmiastowym zamknięciem = flush na dysk):
#   C:\Users\<user>\Desktop\gstarcad-diag-log.txt
# Dzięki temu nawet crash "do pulpitu" zostawia ślad — ostatnia linia pokazuje,
# na czym program stanął.
#
# KOMENDY (wpisuj w linii poleceń GstarCAD po APPLOAD tego pliku):
#   DIAG_INFO      — zapisz nagłówek: wersja GstarCAD, wersja Pythona, maszyna, czas
#   DIAG_VALIDATE  — 15 testów stabilnego podzbioru (nieinteraktywne) → PASS/FAIL każdy
#   DIAG_STRESS    — soak: tysiące operacji w pętlach (hipoteza "kumuluje się w pamięci")
#   DIAG_2DPOLY    — PODEJRZANY crasher: programowa konstrukcja GcDb2dPolyline
#   DIAG_ALL_SAFE  — DIAG_INFO + DIAG_VALIDATE + DIAG_STRESS (bez crashera)
#
# Instrukcja pełna: README-testy-stabilnosci.md w tym samym folderze.
# =====================================================================

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
import sys

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "gstarcad-diag-log.txt")


def _log(msg, truncate=False):
    """Zapis do pliku z natychmiastowym zamknięciem (flush) + do konsoli GstarCAD."""
    try:
        with open(LOG, "w" if truncate else "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
    try:
        gcutPrintf("\n" + msg)
    except Exception:
        pass


def _ms(mode):
    """Otwórz model space. mode = GcDb.kForRead / GcDb.kForWrite."""
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return None
    s, ms = bt.getAt(GCDB_MODEL_SPACE, mode)
    bt.close()
    return ms if s == Gcad.eOk else None


def _sysvar_str(name):
    try:
        rb = resbuf()
        gcedGetVar(name, rb)
        return str(rb.resval.rstring)
    except Exception:
        return "?"


# ---------------------------------------------------------------------
# DIAG_INFO — nagłówek środowiska
# ---------------------------------------------------------------------
@command(local_name='DIAG_INFO')
def diagInfo():
    """Zapisz nagłówek: wersja Pythona, wersja GstarCAD, maszyna. NIE crashuje."""
    try:
        _log("################################################################", truncate=True)
        _log("# GSTARCAD-DIAG — nowa sesja diagnostyczna")
        _log("################################################################")
        try:
            import platform
            _log(f"Maszyna (hostname):  {platform.node()}")
            _log(f"System:              {platform.platform()}")
        except Exception as e:
            _log(f"platform: NIE ({e})")
        _log(f"Python (embedded):   {sys.version.replace(chr(10), ' ')}")
        _log(f"GstarCAD ACADVER:    {_sysvar_str('ACADVER')}")
        _log(f"GstarCAD LOGINNAME:  {_sysvar_str('LOGINNAME')}")
        _log("UWAGA: wersję produktu (np. R27.1.0.2606) i edycję (Premium/Standard/Pro)")
        _log("       dopisz RĘCZNIE z menu Pomoc > O programie.")
        _log("UWAGA: zaznacz czy test LOKALNY (przy maszynie) czy przez RDP — to kluczowe.")
        _log("----------------------------------------------------------------")
    except Exception as err:
        _log(f"DIAG_INFO FAIL: {type(err).__name__}: {err}")


# ---------------------------------------------------------------------
# DIAG_VALIDATE — stabilny podzbiór (15 testów nieinteraktywnych)
# ---------------------------------------------------------------------
def _t(label, fn):
    """Uruchom pojedynczy test, zaloguj PRZED (na wypadek crashu) i PASS/FAIL."""
    _log(f"[TEST] {label} — start")
    try:
        ok, detail = fn()
        _log(f"[{'PASS' if ok else 'FAIL'}] {label} — {detail}")
    except Exception as e:
        _log(f"[FAIL] {label} — WYJATEK {type(e).__name__}: {e}")


@command(local_name='DIAG_VALIDATE')
def diagValidate():
    """15 testów stabilnego podzbioru pygcad. Wszystkie powinny być PASS.
    Jeśli któryś crashuje CAD-a lokalnie — to jest kluczowy wynik dla raportu."""
    _log("=== DIAG_VALIDATE start ===", truncate=False)

    def t_line():
        ms = _ms(GcDb.kForWrite)
        if ms is None:
            return False, "MS open != eOk"
        e = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(100, 100, 0))
        s, i = ms.appendGcDbEntity(e)
        ms.close(); e.close()
        return s == Gcad.eOk, f"append={s}"

    def t_circle():
        ms = _ms(GcDb.kForWrite)
        e = GcDbCircle(GcGePoint3d(50, 50, 0), GcGeVector3d(0, 0, 1), 25.0)
        s, i = ms.appendGcDbEntity(e)
        ms.close(); e.close()
        return s == Gcad.eOk, f"append={s}"

    def t_arc():
        ms = _ms(GcDb.kForWrite)
        e = GcDbArc(GcGePoint3d(0, 0, 0), 30.0, 0.0, 1.57)
        s, i = ms.appendGcDbEntity(e)
        ms.close(); e.close()
        return s == Gcad.eOk, f"append={s}"

    def t_ellipse():
        ms = _ms(GcDb.kForWrite)
        e = GcDbEllipse(GcGePoint3d(0, 0, 0), GcGeVector3d(0, 0, 1), GcGeVector3d(80, 0, 0), 0.5)
        s, i = ms.appendGcDbEntity(e)
        ms.close(); e.close()
        return s == Gcad.eOk, f"append={s}"

    def t_polyline():
        ms = _ms(GcDb.kForWrite)
        p = GcDbPolyline()
        p.addVertexAt(0, GcGePoint2d(0, 0), 0, 0, 0)
        p.addVertexAt(1, GcGePoint2d(100, 0), 0, 0, 0)
        p.addVertexAt(2, GcGePoint2d(100, 60), 0, 0, 0)
        p.addVertexAt(p.numVerts(), GcGePoint2d(0, 0), 0, 0, 0)
        s, i = ms.appendGcDbEntity(p)
        ms.close(); p.close()
        return s == Gcad.eOk, f"wierzch={4}, append={s}"

    def t_text():
        ms = _ms(GcDb.kForWrite)
        e = GcDbText(GcGePoint3d(10, 10, 0), "DIAG")
        e.setHeight(20.0)
        s, i = ms.appendGcDbEntity(e)
        ms.close(); e.close()
        return s == Gcad.eOk, f"GcDbText(pt,str)+setHeight append={s}"

    def t_dim():
        ms = _ms(GcDb.kForWrite)
        e = GcDbAlignedDimension(GcGePoint3d(0, 0, 0), GcGePoint3d(200, 0, 0), GcGePoint3d(100, 80, 0), "DIAG")
        s, i = ms.appendGcDbEntity(e)
        ms.close(); e.close()
        return s == Gcad.eOk, f"append={s}"

    def t_layer():
        db = gcdbWorkingDatabase()
        s, lt = db.getLayerTable(GcDb.kForWrite)
        if s != Gcad.eOk:
            return False, "getLayerTable(W) != eOk"
        if not lt.has("DIAG_L"):
            r = GcDbLayerTableRecord()
            r.setName("DIAG_L")
            c = GcCmColor(); c.setColorIndex(1)
            r.setColor(c)
            lt.add(r); r.close()
        lt.close()
        return True, "GcCmColor+setColor OK"

    def t_layer_read():
        db = gcdbWorkingDatabase()
        s, obj = gcdbOpenObject(db.layerTableId(), GcDb.kForRead)
        tbl = GcDbLayerTable.cast(obj)
        s, it = tbl.newIterator()
        it.start()
        n = 0
        idx = "?"
        while not it.done():
            s, rec = it.getRecord()
            sn, nm = rec.getName()
            if nm == "DIAG_L":
                try:
                    idx = rec.color().colorIndex()
                except Exception:
                    idx = "NIE"
            rec.close()
            n += 1
            it.step()
        tbl.close()
        return True, f"warstw={n}, DIAG_L color().colorIndex()={idx}"

    def t_block():
        db = gcdbWorkingDatabase()
        s, bt = db.getBlockTable(GcDb.kForWrite)
        if not bt.has("DIAG_BLK"):
            bd = GcDbBlockTableRecord()
            bd.setName("DIAG_BLK")
            bt.add(bd)
            l = GcDbLine(GcGePoint3d(-5, 0, 0), GcGePoint3d(5, 0, 0))
            bd.appendGcDbEntity(l); l.close()
            bd.close()
        s, bid = bt.getObjIdAt("DIAG_BLK")
        bt.close()
        ms = _ms(GcDb.kForWrite)
        ref = GcDbBlockReference(GcGePoint3d(150, 150, 0), bid)
        s, i = ms.appendGcDbEntity(ref)
        ms.close(); ref.close()
        return s == Gcad.eOk, f"def+ref append={s}"

    def t_msiter():
        ms = _ms(GcDb.kForRead)
        s, it = ms.newIterator()
        it.start()
        n = 0
        while not it.done():
            s, e = it.getEntity()
            if s == Gcad.eOk and e is not None:
                try:
                    _ = e.isA().name()
                except Exception:
                    pass
                n += 1
            it.step()
        ms.close()
        return True, f"przeiterowano={n}"

    def t_group():
        ms = _ms(GcDb.kForWrite)
        ids = []
        for k in range(2):
            l = GcDbLine(GcGePoint3d(0, k * 10, 0), GcGePoint3d(50, k * 10, 0))
            s, i = ms.appendGcDbEntity(l)
            l.close()
            if s == Gcad.eOk:
                ids.append(i)
        ms.close()
        db = gcdbWorkingDatabase()
        s, gd = db.getGroupDictionary(GcDb.kForWrite)
        g = GcDbGroup("DIAG grupa")
        s, gid = gd.setAt("DIAG_GRP", g)
        gd.close()
        for oid in ids:
            g.append(oid)
        g.close()
        return s == Gcad.eOk, f"dodano={len(ids)}"

    def t_xdata():
        ms = _ms(GcDb.kForWrite)
        l = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(10, 0, 0))
        s, lid = ms.appendGcDbEntity(l)
        l.close(); ms.close()
        gcdbRegApp("DIAG_APP")
        rb = gcutNewRb(1001)
        rb.resval.rstring = "DIAG_APP"
        rb.rbnext = gcutNewRb(1000)
        rb.rbnext.resval.rstring = "diag"
        s, o = gcdbOpenObject(lid, GcDb.kForWrite)
        o.setXData(rb); o.close()
        gcutRelRb(rb)
        s, o2 = gcdbOpenObject(lid, GcDb.kForRead)
        rb2 = o2.xData("DIAG_APP")
        got = "brak"
        if rb2 is not None:
            p = rb2
            while p is not None:
                if p.restype == 1000:
                    got = p.resval.rstring
                p = p.rbnext
            gcutRelRb(rb2)
        o2.close()
        return got == "diag", f"odczyt='{got}'"

    def t_sysvar():
        rb = resbuf()
        gcedGetVar("VIEWSIZE", rb)
        return True, f"VIEWSIZE={rb.resval.rreal}"

    _t("01 linia GcDbLine", t_line)
    _t("02 okrag GcDbCircle", t_circle)
    _t("03 luk GcDbArc", t_arc)
    _t("04 elipsa GcDbEllipse", t_ellipse)
    _t("05 polilinia lekka GcDbPolyline", t_polyline)
    _t("06 tekst GcDbText+setHeight", t_text)
    _t("07 wymiar GcDbAlignedDimension", t_dim)
    _t("08 warstwa GcCmColor+setColor", t_layer)
    _t("09 odczyt warstwy color().colorIndex()", t_layer_read)
    _t("10 blok def+GcDbBlockReference", t_block)
    _t("11 iteracja model space isA().name()", t_msiter)
    _t("12 grupa GcDbGroup+setAt+append", t_group)
    _t("13 XData resbuf+setXData+odczyt", t_xdata)
    _t("14 zmienna systemowa gcedGetVar", t_sysvar)
    _log("=== DIAG_VALIDATE koniec (jeśli widzisz tę linię — BEZ crashu) ===")


# ---------------------------------------------------------------------
# DIAG_STRESS — soak (hipoteza kumulacji w pamięci)
# ---------------------------------------------------------------------
@command(local_name='DIAG_STRESS')
def diagStress():
    """Tysiące operacji w pętlach z licznikiem do pliku. Jeśli crashuje po N
    iteracjach REPRODUKOWALNIE — to sygnał wycieku/kumulacji. Może potrwać minutę."""
    _log("=== DIAG_STRESS start ===", truncate=False)
    try:
        db = gcdbWorkingDatabase()
        # A) open/close tabel
        _log("[STRESS A] open/close tabel x5000")
        for i in range(5000):
            s, bt = db.getBlockTable(GcDb.kForRead)
            if s == Gcad.eOk:
                bt.close()
            if i % 500 == 0:
                _log(f"  A i={i}")
        _log("[STRESS A] koniec BEZ crashu")

        # B) tworzenie encji
        _log("[STRESS B] tworzenie encji x3000")
        for i in range(3000):
            ms = _ms(GcDb.kForWrite)
            if ms is None:
                _log(f"  B i={i}: MS open != eOk (sesja zatruta?)")
                return
            c = GcDbCircle(GcGePoint3d(float(i % 900), float(i % 600), 0), GcGeVector3d(0, 0, 1), 3.0)
            ms.appendGcDbEntity(c); c.close()
            ms.close()
            if i % 300 == 0:
                _log(f"  B i={i}")
        _log("[STRESS B] koniec BEZ crashu")

        # C) iteracja model space
        _log("[STRESS C] iteracja model space x1000")
        for i in range(1000):
            ms = _ms(GcDb.kForRead)
            s, it = ms.newIterator()
            it.start()
            n = 0
            while not it.done():
                s, e = it.getEntity()
                if s == Gcad.eOk and e is not None:
                    n += 1
                it.step()
            ms.close()
            if i % 100 == 0:
                _log(f"  C i={i} obiektow={n}")
        _log("[STRESS C] koniec BEZ crashu")

        # D) warstwy
        _log("[STRESS D] tworzenie warstw x1000")
        for i in range(1000):
            s, lt = db.getLayerTable(GcDb.kForWrite)
            if s != Gcad.eOk:
                _log(f"  D i={i}: getLayerTable != eOk")
                return
            nm = f"DIAG_S{i}"
            if not lt.has(nm):
                r = GcDbLayerTableRecord(); r.setName(nm)
                c = GcCmColor(); c.setColorIndex((i % 7) + 1); r.setColor(c)
                lt.add(r); r.close()
            lt.close()
            if i % 100 == 0:
                _log(f"  D i={i}")
        _log("[STRESS D] koniec BEZ crashu")

        _log("=== DIAG_STRESS koniec: WSZYSTKIE petle BEZ crashu ===")
    except Exception as e:
        _log(f"DIAG_STRESS WYJATEK (NIE crash): {type(e).__name__}: {e}")


# ---------------------------------------------------------------------
# DIAG_2DPOLY — podejrzany crasher (konstrukcja GcDb2dPolyline)
# ---------------------------------------------------------------------
@command(local_name='DIAG_2DPOLY')
def diag2dPoly():
    """PODEJRZANY: programowa konstrukcja GcDb2dPolyline. Na maszynie zdalnej (SP1)
    wszystkie iteracje przechodziły, a CAD crashował na REGENIE po komendzie.
    Instrumentowane per-krok. Jeśli crashuje — plik pokazuje ostatni krok."""
    N = 20
    _log(f"=== DIAG_2DPOLY start N={N} ===", truncate=False)
    try:
        for i in range(N):
            _log(f"i={i}: PRZED GcDb2dPolyline()")
            ms = _ms(GcDb.kForWrite)
            if ms is None:
                _log(f"i={i}: MS open != eOk")
                return
            poly = GcDb2dPolyline()
            s, pid = ms.appendGcDbEntity(poly)
            _log(f"i={i}: PO append (status={s}), PRZED appendVertex")
            for (x, y) in [(0, 0), (100, 0), (100, 50)]:
                v = GcDb2dVertex()
                v.setPosition(GcGePoint3d(float(x), float(y), 0))
                poly.appendVertex(v)
                v.close()
            poly.close()
            ms.close()
            _log(f"i={i}: OK iteracja")
        _log(f"=== DIAG_2DPOLY koniec: {N} iteracji BEZ crashu (uwaga: crash moze przyjsc na REGENIE po komendzie) ===")
    except Exception as e:
        _log(f"DIAG_2DPOLY WYJATEK (NIE crash): {type(e).__name__}: {e}")


# ---------------------------------------------------------------------
# DIAG_ALL_SAFE — INFO + VALIDATE + STRESS (bez crashera)
# ---------------------------------------------------------------------
@command(local_name='DIAG_ALL_SAFE')
def diagAllSafe():
    """Pełny bezpieczny przebieg: nagłówek + walidacja + soak. BEZ DIAG_2DPOLY.
    To jest główny test do wielokrotnego powtarzania na każdej maszynie."""
    diagInfo()
    diagValidate()
    diagStress()
    _log("=== DIAG_ALL_SAFE ZAKONCZONE ===")
    gcutPrintf("\n[DIAG] ALL_SAFE zakonczone — patrz Desktop\\gstarcad-diag-log.txt")
