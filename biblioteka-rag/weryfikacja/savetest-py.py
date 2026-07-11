# Czy pygcad utrwala standalone-bazę PRZEZ TRANSAKCJĘ? (jak .NET przez Commit)
# Bug #2: GcDbDatabase(...)+append+saveAs nie zapisuje encji. .NET z jawnym Commit
# utrwala. Test: czy pygcad z transakcją (db.transactionManager()) też utrwali —
# wtedy folder-batch zostaje czysto w Pythonie i naprawiamy wzorzec 10.
# Każdy wariant zapisuje plik i ODCZYTUJE go z powrotem z dysku. Log: Pulpit\savetest-py.txt
#
# UZYCIE (dowolny rysunek): APPLOAD -> savetest-py.py -> SAVETEST_PY

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

FOLDER = os.path.join("C:\\", "Users", "Public", "savetest-py")
LOG = os.path.join(os.path.expanduser("~"), "Desktop", "savetest-py.txt")


def _log(m, truncate=False):
    try:
        with open(LOG, "w" if truncate else "a", encoding="utf-8") as f:
            f.write(m + "\r\n")
    except Exception:
        pass
    try:
        gcutPrintf("\n" + m)
    except Exception:
        pass


def _ms(db, mode):
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return None
    s, ms = bt.getAt(GCDB_MODEL_SPACE, mode)
    bt.close()
    return ms if s == Gcad.eOk else None


def _read_back(path):
    """Odczyt zapisanego pliku z DYSKU: ile encji tekstowych + treść."""
    try:
        db = GcDbDatabase(False, True)
        st = db.readDwgFile(path)
        if st != Gcad.eOk:
            return f"readDwgFile={st}"
        vals = []
        ms = _ms(db, GcDb.kForRead)
        if ms is None:
            return "brak MS przy odczycie"
        s, it = ms.newIterator()
        it.start()
        while not it.done():
            s, ent = it.getEntity()
            if s == Gcad.eOk and ent is not None:
                try:
                    if "Text" in ent.isA().name():
                        for g in ("textStringConst", "text", "contents"):
                            fn = getattr(ent, g, None)
                            if fn:
                                try:
                                    v = fn()
                                    if isinstance(v, str):
                                        vals.append(v)
                                        break
                                except Exception:
                                    pass
                except Exception:
                    pass
                ent.close()
            it.step()
        ms.close()
        return f"tekstow={len(vals)} {vals}"
    except Exception as e:
        return f"WYJATEK {type(e).__name__}: {e}"


@command(local_name='SAVETEST_PY')
def savetestPy():
    try:
        _log("=== SAVETEST_PY ===", truncate=True)
        if not os.path.isdir(FOLDER):
            os.makedirs(FOLDER)

        # --- V1: baseline (append + saveAs, bez transakcji) — spodziewany FAIL ---
        try:
            p1 = os.path.join(FOLDER, "v1.dwg")
            db = GcDbDatabase(True, True)
            ms = _ms(db, GcDb.kForWrite)
            t = GcDbText(GcGePoint3d(0, 0, 0), "TEXT-V1")
            ms.appendGcDbEntity(t)
            t.close()
            ms.close()
            s1 = db.saveAs(p1)
            _log(f"V1 (append+saveAs):     saveAs={s1} | odczyt: {_read_back(p1)}")
        except Exception as e:
            _log(f"V1 WYJATEK {type(e).__name__}: {e}")

        # --- V2: TRANSAKCJA (jak .NET Commit) ---
        try:
            p2 = os.path.join(FOLDER, "v2.dwg")
            db = GcDbDatabase(True, True)
            tm = db.transactionManager()
            trans = tm.startTransaction()
            ms = _ms(db, GcDb.kForWrite)
            t = GcDbText(GcGePoint3d(0, 0, 0), "TEXT-V2")
            ms.appendGcDbEntity(t)
            ms.close()
            tm.addNewlyCreatedDBRObject(t, True)
            t.close()
            tm.endTransaction()
            s2 = db.saveAs(p2)
            _log(f"V2 (transakcja+saveAs): saveAs={s2} | odczyt: {_read_back(p2)}")
        except Exception as e:
            _log(f"V2 WYJATEK {type(e).__name__}: {e}")

        _log("=== KONIEC ===  (oczek. V? tekstow=1 ['TEXT-V?'] = ten wariant utrwala)")
    except Exception as err:
        _log(f"[BLAD] {type(err).__name__}: {err}")
