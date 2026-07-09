# Sweep 5 — weryfikacja empiryczna prymitywów użytych we wzorcach 03-10.
#
# Cel: rozstrzygnąć pozycje oznaczone 🔴 w przewodniku v2 i README wzorców,
# ZANIM napiszemy wzorce 11-20 na tych samych założeniach. Każdy test jest
# osobną komendą (izolacja — gdyby któryś prymityw crashował CAD do desktopu,
# jak GcDb3dPolyline 1 lipca, tracimy tylko jeden test, nie całą sesję).
#
# Sposób użycia na LightCatcher (GstarCAD 2027 Plus PL, najlepiej też 2026):
#   1. Nowy pusty rysunek (NIE projekt klienta)
#   2. APPLOAD → wybierz ten plik → Load
#   3. Uruchom po kolei komendy i przepisz Dawidowi wynik z command line:
#        VERIFY_TEXT        — konstruktor GcDbText(punkt, str) + setHeight
#        VERIFY_POLY        — GcDbPolyline 2D + addVertexAt (prostokąt)
#        VERIFY_LAYERPROPS  — które properties LayerTableRecord istnieją
#        VERIFY_DIM         — GcDbAlignedDimension(pt1,pt2,pt3,"tekst")
#        VERIFY_BLOCK       — definicja bloku + GcDbBlockReference
#   4. (opcjonalnie) SWEEP5_ALL — odpala wszystkie pięć po kolei
#
# Każda komenda wypisuje [SWEEP5 <nazwa>] PASS/FAIL + szczegół. Interesują nas
# szczególnie: (a) czy PASS, (b) treść FAIL (typ wyjątku), (c) dla LAYERPROPS
# lista która metoda istnieje a która rzuca AttributeError.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _openModelSpace():
    """Zwraca (modelSpace, blockTableClosed?) albo (None, msg)."""
    database = gcdbWorkingDatabase()
    status, blockTable = database.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None, "getBlockTable != eOk"
    status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    blockTable.close()
    if status != Gcad.eOk:
        return None, "getAt(model space) != eOk"
    return modelSpace, None


@command(local_name='VERIFY_TEXT')
def verifyText():
    """🔴 GcDbText(punkt, str) — konstruktor 2-arg + setHeight + append."""
    try:
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP5 TEXT] FAIL (setup): {err}")
            return
        try:
            text = GcDbText(GcGePoint3d(50.0, 50.0, 0.0), "SWEEP5-TEXT")
        except Exception as ctorErr:
            modelSpace.close()
            gcutPrintf(f"\n[SWEEP5 TEXT] FAIL (konstruktor 2-arg): {type(ctorErr).__name__}: {ctorErr}")
            return
        try:
            text.setHeight(25.0)
            height_ok = True
        except Exception as hErr:
            height_ok = f"{type(hErr).__name__}: {hErr}"
        status, tid = modelSpace.appendGcDbEntity(text)
        modelSpace.close()
        text.close()
        gcutPrintf(f"\n[SWEEP5 TEXT] PASS — GcDbText(pt,str) OK, append status={status}, setHeight={height_ok}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP5 TEXT] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_POLY')
def verifyPolyline():
    """🔴 GcDbPolyline 2D + addVertexAt — prostokąt zamknięty przez powrót do startu."""
    try:
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP5 POLY] FAIL (setup): {err}")
            return
        try:
            pline = GcDbPolyline()
            pline.addVertexAt(0, GcGePoint2d(0.0, 0.0), 0, 0, 0)
            pline.addVertexAt(1, GcGePoint2d(100.0, 0.0), 0, 0, 0)
            pline.addVertexAt(2, GcGePoint2d(100.0, 60.0), 0, 0, 0)
            pline.addVertexAt(3, GcGePoint2d(0.0, 60.0), 0, 0, 0)
            pline.addVertexAt(pline.numVerts(), GcGePoint2d(0.0, 0.0), 0, 0, 0)
            nverts = pline.numVerts()
        except Exception as ctorErr:
            modelSpace.close()
            gcutPrintf(f"\n[SWEEP5 POLY] FAIL (budowa): {type(ctorErr).__name__}: {ctorErr}")
            return
        status, pid = modelSpace.appendGcDbEntity(pline)
        modelSpace.close()
        pline.close()
        gcutPrintf(f"\n[SWEEP5 POLY] PASS — GcDbPolyline 2D OK, wierzchołków={nverts}, append status={status}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP5 POLY] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_LAYERPROPS')
def verifyLayerProps():
    """🔴 Które properties LayerTableRecord istnieją: colorIndex/isFrozen/isOff/isLocked/getName."""
    try:
        db = gcdbWorkingDatabase()
        # utwórz warstwę testową z kolorem, żeby mieć co czytać
        status, ltWrite = db.getLayerTable(GcDb.kForWrite)
        if status != Gcad.eOk:
            gcutPrintf("\n[SWEEP5 LAYERPROPS] FAIL: getLayerTable(kForWrite) != eOk")
            return
        if not ltWrite.has("SWEEP5_LAYER"):
            rec = GcDbLayerTableRecord()
            rec.setName("SWEEP5_LAYER")
            col = GcCmColor()
            col.setColorIndex(2)
            rec.setColor(col)
            ltWrite.add(rec)
            rec.close()
        ltWrite.close()

        # teraz iteruj i próbuj czytać każdą property osobno
        status, obj = gcdbOpenObject(db.layerTableId(), GcDb.kForRead)
        table = GcDbLayerTable.cast(obj)
        status, it = table.newIterator()
        it.start()
        results = []
        probed = False
        while not it.done():
            status, rec = it.getRecord()
            sname, name = rec.getName()
            if name == "SWEEP5_LAYER" and not probed:
                probed = True
                for label, fn in [
                    ("getName", lambda: rec.getName()),
                    ("colorIndex", lambda: rec.colorIndex()),
                    ("color", lambda: rec.color()),
                    ("isFrozen", lambda: rec.isFrozen()),
                    ("isOff", lambda: rec.isOff()),
                    ("isLocked", lambda: rec.isLocked()),
                ]:
                    try:
                        val = fn()
                        results.append(f"{label}=OK({val})")
                    except Exception as e:
                        results.append(f"{label}=NIE({type(e).__name__})")
            rec.close()
            it.step()
        table.close()
        gcutPrintf("\n[SWEEP5 LAYERPROPS] " + " | ".join(results))
    except Exception as err:
        gcutPrintf(f"\n[SWEEP5 LAYERPROPS] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_DIM')
def verifyDimension():
    """🟡 GcDbAlignedDimension(pt1, pt2, textPt, str) — per ployline_dim.py."""
    try:
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP5 DIM] FAIL (setup): {err}")
            return
        try:
            pt1 = GcGePoint3d(0.0, 0.0, 0.0)
            pt2 = GcGePoint3d(200.0, 0.0, 0.0)
            pt3 = GcGePoint3d(100.0, 100.0, 0.0)
            dim = GcDbAlignedDimension(pt1, pt2, pt3, "SWEEP5-DIM")
        except Exception as ctorErr:
            modelSpace.close()
            gcutPrintf(f"\n[SWEEP5 DIM] FAIL (konstruktor): {type(ctorErr).__name__}: {ctorErr}")
            return
        status, did = modelSpace.appendGcDbEntity(dim)
        modelSpace.close()
        dim.close()
        gcutPrintf(f"\n[SWEEP5 DIM] PASS — GcDbAlignedDimension OK, append status={status}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP5 DIM] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_BLOCK')
def verifyBlock():
    """🟡 Definicja bloku (GcDbBlockTableRecord) + GcDbBlockReference — per dynBlockTableReference.py."""
    try:
        db = gcdbWorkingDatabase()
        # definicja bloku
        status, btWrite = db.getBlockTable(GcDb.kForWrite)
        if status != Gcad.eOk:
            gcutPrintf("\n[SWEEP5 BLOCK] FAIL: getBlockTable(kForWrite) != eOk")
            return
        if btWrite.has("SWEEP5_BLK"):
            status, blockId = btWrite.getObjIdAt("SWEEP5_BLK")
            btWrite.close()
        else:
            try:
                blockDef = GcDbBlockTableRecord()
                blockDef.setName("SWEEP5_BLK")
                status, blockId = btWrite.add(blockDef)
                btWrite.close()
                l1 = GcDbLine(GcGePoint3d(-10, 0, 0), GcGePoint3d(10, 0, 0))
                blockDef.appendGcDbEntity(l1)
                l1.close()
                l2 = GcDbLine(GcGePoint3d(0, -10, 0), GcGePoint3d(0, 10, 0))
                blockDef.appendGcDbEntity(l2)
                l2.close()
                blockDef.close()
            except Exception as defErr:
                gcutPrintf(f"\n[SWEEP5 BLOCK] FAIL (definicja): {type(defErr).__name__}: {defErr}")
                return
        # referencja bloku
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP5 BLOCK] FAIL (model space): {err}")
            return
        try:
            ref = GcDbBlockReference(GcGePoint3d(150.0, 150.0, 0.0), blockId)
        except Exception as refErr:
            modelSpace.close()
            gcutPrintf(f"\n[SWEEP5 BLOCK] FAIL (GcDbBlockReference): {type(refErr).__name__}: {refErr}")
            return
        status, rid = modelSpace.appendGcDbEntity(ref)
        modelSpace.close()
        ref.close()
        gcutPrintf(f"\n[SWEEP5 BLOCK] PASS — definicja + GcDbBlockReference OK, append status={status}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP5 BLOCK] FAIL: {type(err).__name__}: {err}")


@command(local_name='SWEEP5_ALL')
def sweep5All():
    """Odpala wszystkie pięć testów po kolei. UWAGA: jeśli któryś crashuje CAD,
    użyj komend pojedynczych zamiast tej zbiorczej."""
    gcutPrintf("\n===== SWEEP5 START =====")
    verifyText()
    verifyPolyline()
    verifyLayerProps()
    verifyDimension()
    verifyBlock()
    gcutPrintf("\n===== SWEEP5 KONIEC =====")
