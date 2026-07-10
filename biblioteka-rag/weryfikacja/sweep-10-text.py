# Sweep 10 — walidacja manipulacji TEKSTEM (fundament wzorców-rdzenia Fazy A).
#
# Wzorce workhorse (batch find-replace, atrybuty, renumeracja) stoją na czytaniu
# i zapisie stringów encji tekstowych. Stuby pokazują niejednoznaczne API:
#   GcDbText.setTextString(str)->ErrorStatus  ORAZ  textString(GcString)->ErrorStatus (out-param)
#   GcDbMText.text()->str / text(GcString)->ErrorStatus / contents()->str
#   GcDbAttribute(GcDbText) + tag()
#   GcDbBlockReference.attributeIterator() + openAttribute(id, mode)
# Ten sweep potwierdza empirycznie, KTÓRA forma działa w Pythonie — zanim zbudujemy
# na tym batch-wzorce. Log do pliku (przeżywa crash): Desktop\sweep10-text.txt.
#
# UŻYCIE (nowy pusty rysunek):
#   APPLOAD -> sweep-10-text.py -> Load
#   VERIFY_TEXT_RW      — GcDbText: zapis stringa, odczyt (5 wariantów getterów)
#   VERIFY_MTEXT_RW     — GcDbMText: zapis + odczyt (text()/contents())
#   VERIFY_ATTR_RW      — blok z atrybutem: iteracja + odczyt/zapis tagu i wartości
#   SWEEP10_ALL

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

LOG = os.path.join(os.path.expanduser("~"), "Desktop", "sweep10-text.txt")


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


def _ms(mode):
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    if s != Gcad.eOk:
        return None
    s, ms = bt.getAt(GCDB_MODEL_SPACE, mode)
    bt.close()
    return ms if s == Gcad.eOk else None


def _probe(label, fn):
    try:
        val = fn()
        _log(f"  {label} = OK -> {repr(val)}")
        return val
    except Exception as e:
        _log(f"  {label} = NIE ({type(e).__name__}: {e})")
        return None


@command(local_name='VERIFY_TEXT_RW')
def verifyTextRw():
    """GcDbText: utwórz z tekstem, potem próbuj różnych form odczytu; zmień i odczytaj."""
    try:
        _log("=== TEXT_RW start ===", truncate=True)
        ms = _ms(GcDb.kForWrite)
        if ms is None:
            _log("FAIL: MS open")
            return
        t = GcDbText(GcGePoint3d(0, 0, 0), "ALFA-123")
        s, tid = ms.appendGcDbEntity(t)
        t.close()
        ms.close()

        _log("[ODCZYT] próbuję formy getterów na 'ALFA-123':")
        s, obj = gcdbOpenObject(tid, GcDb.kForRead)
        _probe("textString() [bez arg, jako str]", lambda: obj.textString())
        _probe("textStringConst()", lambda: obj.textStringConst())
        def _viaGcString():
            gs = GcString()
            st = obj.textString(gs)
            return str(gs)
        _probe("textString(GcString)->str(gs)", _viaGcString)
        obj.close()

        _log("[ZAPIS] setTextString('BETA-999'):")
        s, obj2 = gcdbOpenObject(tid, GcDb.kForWrite)
        _probe("setTextString('BETA-999')", lambda: obj2.setTextString("BETA-999"))
        obj2.close()

        _log("[ODCZYT po zapisie] czy = BETA-999:")
        s, obj3 = gcdbOpenObject(tid, GcDb.kForRead)
        _probe("textStringConst() po zapisie", lambda: obj3.textStringConst())
        obj3.close()
        _log("=== TEXT_RW koniec (bez crashu) ===")
    except Exception as err:
        _log(f"FAIL TEXT_RW: {type(err).__name__}: {err}")


@command(local_name='VERIFY_MTEXT_RW')
def verifyMtextRw():
    """GcDbMText: utwórz, odczytaj text()/contents(), zmień, odczytaj."""
    try:
        _log("=== MTEXT_RW start ===")
        ms = _ms(GcDb.kForWrite)
        if ms is None:
            _log("FAIL: MS open")
            return
        try:
            m = GcDbMText()
            m.setLocation(GcGePoint3d(0, 50, 0))
            m.setContents("MTEXT-ALFA")
            ctor_ok = "OK"
        except Exception as e:
            _log(f"  konstrukcja MText NIE ({type(e).__name__}: {e})")
            ms.close()
            return
        s, mid = ms.appendGcDbEntity(m)
        m.close()
        ms.close()

        _log("[ODCZYT] formy:")
        s, obj = gcdbOpenObject(mid, GcDb.kForRead)
        _probe("text() [str]", lambda: obj.text())
        _probe("contents() [str]", lambda: obj.contents())
        obj.close()

        _log("[ZAPIS] setContents('MTEXT-BETA'):")
        s, obj2 = gcdbOpenObject(mid, GcDb.kForWrite)
        _probe("setContents('MTEXT-BETA')", lambda: obj2.setContents("MTEXT-BETA"))
        obj2.close()

        s, obj3 = gcdbOpenObject(mid, GcDb.kForRead)
        _probe("contents() po zapisie", lambda: obj3.contents())
        obj3.close()
        _log("=== MTEXT_RW koniec (bez crashu) ===")
    except Exception as err:
        _log(f"FAIL MTEXT_RW: {type(err).__name__}: {err}")


@command(local_name='VERIFY_ATTR_RW')
def verifyAttrRw():
    """Blok z definicją atrybutu + referencja z atrybutem: iteracja + odczyt/zapis wartości."""
    try:
        _log("=== ATTR_RW start ===")
        db = gcdbWorkingDatabase()
        s, bt = db.getBlockTable(GcDb.kForWrite)
        if s != Gcad.eOk:
            _log("FAIL: getBlockTable(W)")
            return
        # definicja bloku z definicją atrybutu
        if not bt.has("SWEEP10_BLK"):
            bd = GcDbBlockTableRecord()
            bd.setName("SWEEP10_BLK")
            bt.add(bd)
            try:
                ad = GcDbAttributeDefinition()
                ad.setTextString("DEFAULT")
                ad.setTag("NUMER")
                ad.setPosition(GcGePoint3d(0, 0, 0))
                ad.setHeight(2.5)
                bd.appendGcDbEntity(ad)
                ad.close()
                _log("  definicja atrybutu NUMER dodana")
            except Exception as e:
                _log(f"  GcDbAttributeDefinition NIE ({type(e).__name__}: {e})")
            bd.close()
        s, bid = bt.getObjIdAt("SWEEP10_BLK")
        bt.close()

        # referencja bloku + dołączenie atrybutu
        ms = _ms(GcDb.kForWrite)
        ref = GcDbBlockReference(GcGePoint3d(100, 100, 0), bid)
        s, rid = ms.appendGcDbEntity(ref)
        _log("  referencja wstawiona; próbuję dołączyć atrybut:")
        try:
            attr = GcDbAttribute()
            attr.setTag("NUMER")
            attr.setTextString("A-001")
            attr.setPosition(GcGePoint3d(100, 100, 0))
            attr.setHeight(2.5)
            _probe("ref.appendAttribute(attr)", lambda: ref.appendAttribute(attr))
            attr.close()
        except Exception as e:
            _log(f"  GcDbAttribute NIE ({type(e).__name__}: {e})")
        ref.close()
        ms.close()

        # iteracja atrybutów referencji + odczyt/zapis
        _log("[ITERACJA] atrybutów referencji:")
        s, robj = gcdbOpenObject(rid, GcDb.kForRead)
        try:
            it = robj.attributeIterator()
            n = 0
            while not it.done():
                aid = it.objectId()
                s2, a = robj.openAttribute(aid, GcDb.kForRead)
                _probe(f"attr[{n}] tag()", lambda: a.tag())
                _probe(f"attr[{n}] textStringConst()", lambda: a.textStringConst())
                a.close()
                n += 1
                it.step()
            _log(f"  atrybutów przeiterowano: {n}")
        except Exception as e:
            _log(f"  attributeIterator NIE ({type(e).__name__}: {e})")
        robj.close()
        _log("=== ATTR_RW koniec (bez crashu) ===")
    except Exception as err:
        _log(f"FAIL ATTR_RW: {type(err).__name__}: {err}")


@command(local_name='SWEEP10_ALL')
def sweep10All():
    gcutPrintf("\n===== SWEEP10 START =====")
    verifyTextRw()
    verifyMtextRw()
    verifyAttrRw()
    gcutPrintf("\n===== SWEEP10 KONIEC =====")
