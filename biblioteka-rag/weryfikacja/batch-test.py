# Test folder-batch: zamiana tekstu w wielu plikach .dwg BEZ otwierania w edytorze.
# Bada niezbadane API: zapis na bazie doczytanej readDwgFile (side-db), przez
# iterator.getEntity(kForWrite) (stub: getEntity przyjmuje openMode). saveAs(path, True)
# robi .bak. Samowystarczalny: BATCH_SEED tworzy pliki, BATCH_ZAMIEN je przetwarza,
# BATCH_VERIFY odczytuje z powrotem. Log (flush): Desktop\batch-test.txt
#
# UZYCIE (dowolny rysunek): APPLOAD -> batch-test.py ->
#   BATCH_SEED     (tworzy C:\Users\Public\batch-test\plik1..3.dwg z tekstem BETA)
#   BATCH_ZAMIEN   (folder-batch BETA->GAMMA, oczek. 2 zamiany/plik, +.bak)
#   BATCH_VERIFY   (odczyt: teksty powinny byc GAMMA)

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

FOLDER = os.path.join("C:\\", "Users", "Public", "batch-test")
LOG = os.path.join(os.path.expanduser("~"), "Desktop", "batch-test.txt")


def _log(msg, truncate=False):
    try:
        with open(LOG, "w" if truncate else "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
    try:
        gcutPrintf("\n" + msg)
    except Exception:
        pass


def _get_str(ent):
    for g in ("textStringConst", "text", "contents"):
        fn = getattr(ent, g, None)
        if fn is None:
            continue
        try:
            v = fn()
            if isinstance(v, str):
                return v
        except Exception:
            continue
    return None


def _set_str(ent, s):
    for st in ("setTextString", "setContents"):
        fn = getattr(ent, st, None)
        if fn is None:
            continue
        try:
            fn(s)
            return True
        except Exception:
            continue
    return False


def _seed_one(path, i):
    db = GcDbDatabase(True, True)  # noDocument=True -> standalone baza do zapisu
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return f"getBlockTable={s}"
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if s != Gcad.eOk:
        return f"getAt(MS)={s}"
    t = GcDbText(GcGePoint3d(0, 0, 0), f"BETA-{i}")
    sa, tid = ms.appendGcDbEntity(t)
    _log(f"    append(text)={sa}")
    t.close()
    m = GcDbMText()
    m.setLocation(GcGePoint3d(0, 50, 0))
    m.setContents(f"MTEXT-BETA-{i}")
    sm, mid = ms.appendGcDbEntity(m)
    _log(f"    append(mtext)={sm}")
    m.close()
    # policz encje w MS PRZED zapisem (czy w ogóle tam są?)
    cnt = 0
    s2, it = ms.newIterator()
    it.start()
    while not it.done():
        cnt += 1
        it.step()
    _log(f"    encji w MS przed saveAs: {cnt}")
    ms.close()
    return db.saveAs(path)


def _dwg_files():
    try:
        return sorted(n for n in os.listdir(FOLDER) if n.lower().endswith(".dwg"))
    except Exception:
        return []


@command(local_name='BATCH_SEED')
def batchSeed():
    try:
        _log("===== BATCH_SEED =====", truncate=True)
        if not os.path.isdir(FOLDER):
            os.makedirs(FOLDER)
        for i in (1, 2, 3):
            path = os.path.join(FOLDER, f"plik{i}.dwg")
            st = _seed_one(path, i)
            _log(f"  plik{i}.dwg saveAs -> {st}")
        _log(f"  pliki w folderze: {_dwg_files()}")
    except Exception as err:
        _log(f"[BLAD SEED] {type(err).__name__}: {err}")


def _replace_in_db(db, find, repl):
    """Zamiana w bazie side-db (doczytanej readDwgFile). Zwraca liczbe zamian.
    Klucz: iterator.getEntity(kForWrite) otwiera encje do ZAPISU wprost."""
    n = 0
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return 0, f"getBlockTable={s}"
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if s != Gcad.eOk:
        return 0, f"getAt(MS)={s}"
    s, it = ms.newIterator()
    it.start()
    first = True
    while not it.done():
        sg, ent = it.getEntity(GcDb.kForWrite)
        if first:
            _log(f"    getEntity(kForWrite) status={sg}")
            first = False
        if sg == Gcad.eOk and ent is not None:
            try:
                cls = ent.isA().name()
            except Exception:
                cls = ""
            if "Text" in cls and "Attribute" not in cls:
                cur = _get_str(ent)
                if cur and find in cur and _set_str(ent, cur.replace(find, repl)):
                    n += 1
            ent.close()
        it.step()
    ms.close()
    return n, "ok"


@command(local_name='BATCH_ZAMIEN')
def batchZamien():
    find, repl = "BETA", "GAMMA"
    try:
        _log("===== BATCH_ZAMIEN (BETA->GAMMA) =====")
        files = _dwg_files()
        if not files:
            _log(f"  brak .dwg w {FOLDER} — najpierw BATCH_SEED")
            return
        total = 0
        for name in files:
            path = os.path.join(FOLDER, name)
            db = GcDbDatabase(False, False)
            st = db.readDwgFile(path)
            if st != Gcad.eOk:
                _log(f"  {name}: readDwgFile -> {st} (POMIJAM)")
                continue
            n, info = _replace_in_db(db, find, repl)
            st2 = db.saveAs(path, True)  # bBakAndRename=True -> .bak
            total += n
            _log(f"  {name}: zamian={n} ({info}) saveAs(+bak)={st2}")
        _log(f"  RAZEM zamian: {total} (oczek. {2 * len(files)})")
    except Exception as err:
        _log(f"[BLAD ZAMIEN] {type(err).__name__}: {err}")


@command(local_name='BATCH_VERIFY')
def batchVerify():
    try:
        _log("===== BATCH_VERIFY (odczyt) =====")
        for name in _dwg_files():
            path = os.path.join(FOLDER, name)
            db = GcDbDatabase(False, False)
            st = db.readDwgFile(path)
            if st != Gcad.eOk:
                _log(f"  {name}: readDwgFile -> {st}")
                continue
            vals = []
            s, bt = db.getBlockTable(GcDb.kForRead)
            if s == Gcad.eOk:
                s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
                bt.close()
                if s == Gcad.eOk:
                    s, it = ms.newIterator()
                    it.start()
                    while not it.done():
                        sg, ent = it.getEntity()
                        if sg == Gcad.eOk and ent is not None:
                            v = _get_str(ent)
                            if v:
                                vals.append(v)
                            ent.close()
                        it.step()
                    ms.close()
            _log(f"  {name}: {vals}")
    except Exception as err:
        _log(f"[BLAD VERIFY] {type(err).__name__}: {err}")
