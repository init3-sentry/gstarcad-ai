# -*- coding: utf-8 -*-
# Logika GSAI_XYZ -> importxyz_logic.pyd (Cython). NIE importuje pygcad;
# loader podaje globals(), tu globals().update(api). Nazwy API pre-deklarowane (Cython).
#
# ⚠️ TO JEST SZABLON WZORCA SZYFROWANIA, NIE DZIAŁAJĄCE NARZĘDZIE.
# Zamrożony 2026-07-14, pokazuje wyłącznie mechanikę loader→globals()→.pyd.
# Logika importu jest tu STARA i ma znany błąd: pyta o format słowem kluczowym,
# a „N" trafia w NrXY zamiast NrXYZ i po cichu wyrzuca kolumnę Z (Tomasz, 2026-07-17).
#
# SoT logiki = `biblioteka-rag/przyklady/25_import_coordinates.py` (format rozpoznawany
# z zawartości pliku). Budując płatny suite jako .pyd: weź WZORZEC stąd, LOGIKĘ z SoT.
import re

# API pygcad — deklaracja (Cython), realne wartosci z loadera przez globals().update:
gcdbWorkingDatabase = GcDb = Gcad = GCDB_MODEL_SPACE = None
resbuf = RTSHORT = RTREAL = gcedSetVar = None
gcedGetFileD = RTNORM = gcedGetString = None
gcedInitGet = gcedGetKword = RTNONE = None
GcGePoint3d = GcDbPoint = GcDbText = gcutPrintf = None


def run(api):
    globals().update(api)
    _importxyz()


def _openModelSpace():
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None, None
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if status != Gcad.eOk:
        return None, None
    return ms, db


def _setPointDisplayVars():
    try:
        rb = resbuf()
        rb.restype = RTSHORT
        rb.resval.rint = 3
        gcedSetVar("PDMODE", rb)
        rb2 = resbuf()
        rb2.restype = RTREAL
        rb2.resval.rreal = -2.0
        gcedSetVar("PDSIZE", rb2)
    except Exception:
        pass


def _parseLine(raw, fmt):
    line = raw.strip()
    if not line or line.startswith("#") or line.startswith("//"):
        return None
    if ";" in line or "\t" in line:
        toks = [t.strip() for t in re.split(r"[;\t]+", line) if t.strip()]
    else:
        toks = [t.strip() for t in re.split(r"\s+", line) if t.strip()]
    if not toks:
        return None

    def num(tok):
        return float(tok.replace(",", "."))

    try:
        if fmt == "XY":
            return (None, num(toks[0]), num(toks[1]), 0.0)
        if fmt == "XYZ":
            return (None, num(toks[0]), num(toks[1]), num(toks[2]))
        if fmt == "NrXY":
            return (toks[0], num(toks[1]), num(toks[2]), 0.0)
        if fmt == "NrXYZ":
            return (toks[0], num(toks[1]), num(toks[2]), num(toks[3]))
    except (ValueError, IndexError):
        return None
    return None


def _readRows(path, fmt):
    data = None
    for enc in ("utf-8-sig", "cp1250", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as fp:
                data = fp.readlines()
            break
        except (UnicodeDecodeError, OSError):
            continue
    if data is None:
        return None, 0
    rows, skipped = [], 0
    auto = 0
    for raw in data:
        parsed = _parseLine(raw, fmt)
        if parsed is None:
            if raw.strip() and not raw.strip().startswith(("#", "//")):
                skipped += 1
            continue
        label, x, y, z = parsed
        if label is None:
            auto += 1
            label = str(auto)
        rows.append((label, x, y, z))
    return rows, skipped


def _importxyz():
    try:
        path = None
        okno_ok = True
        try:
            rbf = resbuf()
            rc = gcedGetFileD("Wybierz plik ze wspolrzednymi (CSV / TXT)", "", "csv;txt", 0, rbf)
        except Exception:
            okno_ok = False
            rc = None
        if okno_ok:
            if rc == RTNORM:
                try:
                    path = rbf.resval.rstring
                except Exception:
                    path = None
            else:
                gcutPrintf("\nAnulowano (nie wybrano pliku).")
                return
        if not path:
            status, path = gcedGetString(1, "\nPodaj sciezke do pliku ze wspolrzednymi: ")
            if status != RTNORM or not path or not path.strip():
                gcutPrintf("\nAnulowano.")
                return
        path = path.strip().strip('"')

        gcedInitGet(0, "XY XYZ NrXY NrXYZ")
        rc, kw = gcedGetKword("\nFormat pliku [XY/XYZ/NrXY/NrXYZ] <NrXY>: ")
        if rc == RTNONE:
            fmt = "NrXY"
        elif rc == RTNORM and kw in ("XY", "XYZ", "NrXY", "NrXYZ"):
            fmt = kw
        else:
            gcutPrintf("\nAnulowano.")
            return

        rows, skipped = _readRows(path, fmt)
        if rows is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc pliku: %s" % path)
            return
        if not rows:
            gcutPrintf("\n[IMPORTXYZ] Zero poprawnych wierszy w formacie %s (pominieto %d)." % (fmt, skipped))
            return

        xs = [r[1] for r in rows]
        ys = [r[2] for r in rows]
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        txtH = (span * 0.02) if span > 1e-6 else 2.5
        off = txtH * 0.6

        ms, _ = _openModelSpace()
        if ms is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc przestrzeni modelu.")
            return

        placed = 0
        for label, x, y, z in rows:
            pt = GcGePoint3d(x, y, z)
            point = GcDbPoint(pt)
            ms.appendGcDbEntity(point)
            point.close()
            txt = GcDbText(GcGePoint3d(x + off, y + off, z), str(label))
            txt.setHeight(txtH)
            ms.appendGcDbEntity(txt)
            txt.close()
            placed += 1

        ms.close()
        _setPointDisplayVars()

        gcutPrintf("\n[IMPORTXYZ z .pyd] Wstawiono %d punktow (format %s, pominieto %d)." % (placed, fmt, skipped))
        gcutPrintf("\n[IMPORTXYZ] Wpisz ZOOM, potem A, zeby zobaczyc punkty.")

    except Exception as err:
        gcutPrintf("\n[IMPORTXYZ BLAD] %s: %s" % (type(err).__name__, str(err)))
