# Wzorzec 21 (★ RDZEŃ workhorse, Faza A) — Znajdź i zamień tekst.
#
# Kierunek zatwierdzony po researchu (research/05-decyzje.md): batch operacje na
# tekście = rdzeń wartości (rank #1, 24/25). GstarCAD ma natywne Find&Replace,
# ale TYLKO w jednym rysunku i bez reguł/semantyki — nasza wartość to: (a) batch
# przez wiele plików, (b) reguła/semantyka opisana po ludzku (LLM generuje z opisu).
#
# STATUS: ✅ ZWALIDOWANY end-to-end na LC 2026-07-10 (GstarCAD 2027 SP1, R27.1.0.2606)
# przez weryfikacja/waliduj-petla.py — 10/10 iteracji PASS (zamiana=2 za każdym razem,
# bez eNotOpenForWrite). Lekcja: iterator zwraca encje do ODCZYTU — zapis wymaga
# zebrania ObjectId i ponownego otwarcia encji do ZAPISU (patrz _replace_in_current_db).
# Wariant FOLDER-BATCH (na dole pliku) pozostaje 🟡 — nie odpalony end-to-end.
#
# Sposób użycia: APPLOAD, następnie ZAMIEN_TEKST. Komenda pyta o szukany tekst
# i tekst docelowy, po czym podmienia we WSZYSTKICH tekstach/mtekstach/atrybutach
# bieżącego rysunku. Wariant folder-batch (wiele plików) — patrz sekcja na dole.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _get_str(ent):
    """Odczyt stringa z encji tekstowej (GcDbText/GcDbMText/GcDbAttribute) — defensywnie.
    Zwraca str albo None. Formy do potwierdzenia sweep-10 (textStringConst / text / contents)."""
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
    """Zapis stringa do encji tekstowej — defensywnie. Zwraca True przy sukcesie."""
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


def _replace_in_current_db(database, find, repl):
    """Znajdź i zamień w bieżącej bazie: teksty, mteksty, atrybuty referencji bloków.
    Zwraca liczbę podmian.

    UWAGA (empiria 2026-07-10): iterator zwraca encje otwarte do ODCZYTU — zapis na
    nich = 'Internal Error: eNotOpenForWrite'. Dlatego dwa kroki: (1) zbierz ObjectId
    przy odczycie i zamknij kontener, (2) otwórz każdą encję OSOBNO do zapisu.
    """
    count = 0
    # 1) Zbierz ObjectId wszystkich encji w model space (odczyt), potem zamknij.
    s, bt = database.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return 0
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
    bt.close()
    if s != Gcad.eOk:
        return 0
    ids = []
    s, it = ms.newIterator()
    it.start()
    while not it.done():
        s, ent = it.getEntity()
        if s == Gcad.eOk and ent is not None:
            try:
                ids.append(ent.objectId())
            except Exception:
                pass
            ent.close()
        it.step()
    ms.close()

    # 2) Otwórz każdą encję do ZAPISU i podmień.
    for oid in ids:
        s, ent = gcdbOpenObject(oid, GcDb.kForWrite)
        if s != Gcad.eOk or ent is None:
            continue
        try:
            cls = ent.isA().name()
        except Exception:
            cls = ""
        # Teksty i mteksty — bezpośrednio (ent otwarta do zapisu)
        if "Text" in cls and "Attribute" not in cls:
            cur = _get_str(ent)
            if cur is not None and find in cur:
                if _set_str(ent, cur.replace(find, repl)):
                    count += 1
        # Referencje bloków — iteruj ich atrybuty (ref już otwarta do zapisu)
        elif "BlockReference" in cls:
            try:
                ait = ent.attributeIterator()
                while not ait.done():
                    aid = ait.objectId()
                    sa, attr = ent.openAttribute(aid, GcDb.kForWrite)
                    if sa == Gcad.eOk and attr is not None:
                        cur = _get_str(attr)
                        if cur is not None and find in cur:
                            if _set_str(attr, cur.replace(find, repl)):
                                count += 1
                        attr.close()
                    ait.step()
            except Exception:
                pass
        ent.close()
    return count


@command(local_name='ZAMIEN_TEKST')
def batchFindReplace():
    """Znajdź i zamień tekst we wszystkich tekstach/mtekstach/atrybutach bieżącego rysunku."""
    try:
        status, find = gcedGetString(1, "\nSzukany tekst: ")   # 1 = zezwól na spacje
        if status != RTNORM or not find:
            gcutPrintf("\nAnulowano.")
            return
        status, repl = gcedGetString(1, "\nZamień na: ")
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        n = _replace_in_current_db(gcdbWorkingDatabase(), find, repl)
        gcutPrintf(f"\nZamieniono '{find}' -> '{repl}' w {n} miejscach.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy zamianie tekstu: {err}")


# =====================================================================
# WARIANT FOLDER-BATCH (★ realna wartość #1 — wiele rysunków naraz). 🟡 do walidacji.
# Przetwarza wszystkie .dwg w folderze BEZ otwierania ich w edytorze:
# każdy plik -> GcDbDatabase(False,False) + readDwgFile -> _replace_in_current_db-owy
# odpowiednik na tej bazie -> saveAs. Prymitywy readDwgFile/saveAs są zwalidowane
# (wzorzec 17/sweep-9); podmiana tekstu na NIE-aktywnej bazie do potwierdzenia na LC.
# Szkielet (po walidacji sweep-10 + testach batch przeniesiemy do osobnej komendy
# BATCH_ZAMIEN_TEKST z pytaniem o ścieżkę folderu):
#
#   import os
#   for name in os.listdir(folder):
#       if not name.lower().endswith(".dwg"): continue
#       path = os.path.join(folder, name)
#       db = GcDbDatabase(False, False)
#       if db.readDwgFile(path) != Gcad.eOk: continue
#       n = _replace_in_db(db, find, repl)     # wariant _replace_in_current_db na 'db'
#       if n: db.saveAs(path)
# =====================================================================
