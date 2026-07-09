# Sweep 6 — weryfikacja empiryczna prymitywów użytych we wzorcach 11-14.
#
# Cel: rozstrzygnąć czy prymitywy wzorców 11-14 działają, ZANIM je opublikujemy.
# Testujemy je BEZ interaktywnego zaznaczania (gcedEntSel/gcedSSGet dają RTNORM —
# to już potwierdzone w sweep-5/wzorcu 05); tu sprawdzamy część "za selekcją".
# Każdy test = osobna komenda (izolacja). Uruchamiaj na NOWYM pustym rysunku;
# jeśli któryś FAIL zatruje sesję (niezamknięta tabela), zrób Ctrl+N przed kolejnym.
#
# Sposób użycia na LightCatcher (GstarCAD 2027 Plus PL):
#   1. Nowy pusty rysunek
#   2. APPLOAD -> sweep-6-verify.py -> Load
#   3. Uruchom po kolei i przepisz wynik:
#        VERIFY_RGB_LAYER  — GcCmColor.setRGB + record.setColor + entity.setLayer   (wzorzec 11)
#        VERIFY_MSITER     — iteracja model space: newIterator+getEntity+isA().name() (wzorzec 12)
#        VERIFY_2DPOLY     — GcDb2dPolyline: utworzenie + vertexIterator + position() (wzorzec 13)
#        VERIFY_GROUP      — getGroupDictionary + GcDbGroup + setAt + append          (wzorzec 14)
#   4. (opcjonalnie) SWEEP6_ALL — wszystkie po kolei

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _openModelSpace(mode=None):
    """Zwraca (modelSpace, None) albo (None, msg). mode domyślnie kForWrite."""
    if mode is None:
        mode = GcDb.kForWrite
    database = gcdbWorkingDatabase()
    status, blockTable = database.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None, "getBlockTable != eOk"
    status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, mode)
    blockTable.close()
    if status != Gcad.eOk:
        return None, "getAt(model space) != eOk"
    return modelSpace, None


@command(local_name='VERIFY_RGB_LAYER')
def verifyRgbLayer():
    """wzorzec 11: kolor warstwy przez setRGB + przypisanie encji przez setLayer."""
    try:
        db = gcdbWorkingDatabase()
        status, lt = db.getLayerTable(GcDb.kForWrite)
        if status != Gcad.eOk:
            gcutPrintf("\n[SWEEP6 RGB_LAYER] FAIL: getLayerTable(kForWrite) != eOk")
            return
        rgb_ok = "?"
        if not lt.has("SWEEP6_RGB"):
            rec = GcDbLayerTableRecord()
            rec.setName("SWEEP6_RGB")
            try:
                col = GcCmColor()
                col.setRGB(0, 128, 255)
                rec.setColor(col)
                rgb_ok = "OK"
            except Exception as e:
                rgb_ok = f"NIE({type(e).__name__})"
            lt.add(rec)
            rec.close()
        lt.close()

        # utwórz linię i przypisz do warstwy przez setLayer
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP6 RGB_LAYER] FAIL (model space): {err}")
            return
        line = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(500, 0, 0))
        status, lid = modelSpace.appendGcDbEntity(line)
        try:
            line.setLayer("SWEEP6_RGB")
            setlayer_ok = "OK"
        except Exception as e:
            setlayer_ok = f"NIE({type(e).__name__})"
        modelSpace.close()
        line.close()
        gcutPrintf(f"\n[SWEEP6 RGB_LAYER] PASS — setRGB={rgb_ok}, setLayer={setlayer_ok}, append={status}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP6 RGB_LAYER] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_MSITER')
def verifyModelSpaceIteration():
    """wzorzec 12: iteracja model space + klasyfikacja isA().name()."""
    try:
        # najpierw dodaj 2 encje, żeby było co liczyć
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP6 MSITER] FAIL (setup): {err}")
            return
        c = GcDbCircle(GcGePoint3d(100, 100, 0), GcGeVector3d(0, 0, 1), 40)
        modelSpace.appendGcDbEntity(c)
        c.close()
        l = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(200, 0, 0))
        modelSpace.appendGcDbEntity(l)
        l.close()
        modelSpace.close()

        # teraz iteruj i klasyfikuj
        modelSpace, err = _openModelSpace(GcDb.kForRead)
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP6 MSITER] FAIL (reopen): {err}")
            return
        status, it = modelSpace.newIterator()
        if status != Gcad.eOk:
            modelSpace.close()
            gcutPrintf("\n[SWEEP6 MSITER] FAIL: newIterator != eOk")
            return
        counts = {}
        total = 0
        it.start()
        while not it.done():
            status, ent = it.getEntity()
            if status == Gcad.eOk and ent is not None:
                try:
                    nm = ent.isA().name()
                except Exception:
                    nm = "(brak isA)"
                counts[nm] = counts.get(nm, 0) + 1
                total += 1
            it.step()
        modelSpace.close()
        summary = ", ".join(f"{k}={v}" for k, v in counts.items())
        gcutPrintf(f"\n[SWEEP6 MSITER] PASS — obiektów={total} | {summary}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP6 MSITER] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_2DPOLY')
def verify2dPolyline():
    """wzorzec 13: utworzenie GcDb2dPolyline + odczyt wierzchołków przez vertexIterator."""
    try:
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP6 2DPOLY] FAIL (setup): {err}")
            return
        # utworzenie: GcDb2dPolyline musi trafić do bazy zanim dodamy wierzchołki
        try:
            poly = GcDb2dPolyline()
        except Exception as e:
            modelSpace.close()
            gcutPrintf(f"\n[SWEEP6 2DPOLY] FAIL (konstruktor GcDb2dPolyline): {type(e).__name__}: {e}")
            return
        status, polyId = modelSpace.appendGcDbEntity(poly)
        # dodaj wierzchołki do polilinii już w bazie
        vtx_ok = "OK"
        try:
            for (x, y) in [(0, 0), (300, 0), (300, 200), (0, 200)]:
                v = GcDb2dVertex()
                v.setPosition(GcGePoint3d(x, y, 0))
                poly.appendVertex(v)
                v.close()
        except Exception as e:
            vtx_ok = f"NIE({type(e).__name__}: {e})"
        poly.close()
        modelSpace.close()

        if vtx_ok != "OK":
            gcutPrintf(f"\n[SWEEP6 2DPOLY] czesciowo — utworzenie OK, dodawanie wierzcholkow: {vtx_ok}")
            return

        # odczyt wierzchołków (per pliniter.py)
        status, obj = gcdbOpenObject(polyId, GcDb.kForRead)
        read_count = 0
        if obj.isKindOf(GcDb2dPolyline.desc()):
            vit = obj.vertexIterator()
            obj.close()
            while not vit.done():
                vid = vit.objectId()
                status, vo = gcdbOpenObject(vid, GcDb.kForRead)
                vtx = GcDb2dVertex.cast(vo)
                _ = vtx.position()
                vtx.close()
                read_count += 1
                vit.step()
        else:
            obj.close()
            gcutPrintf("\n[SWEEP6 2DPOLY] FAIL: utworzony obiekt nie jest GcDb2dPolyline")
            return
        gcutPrintf(f"\n[SWEEP6 2DPOLY] PASS — utworzono + odczytano wierzchołków={read_count}")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP6 2DPOLY] FAIL: {type(err).__name__}: {err}")


@command(local_name='VERIFY_GROUP')
def verifyGroup():
    """wzorzec 14: słownik grup + GcDbGroup + setAt + append (bez interaktywnej selekcji)."""
    try:
        # utwórz 2 encje i zbierz ich ObjectId
        modelSpace, err = _openModelSpace()
        if modelSpace is None:
            gcutPrintf(f"\n[SWEEP6 GROUP] FAIL (setup): {err}")
            return
        ids = []
        for (x0, x1) in [(0, 100), (0, 100)]:
            ln = GcDbLine(GcGePoint3d(x0, len(ids) * 50, 0), GcGePoint3d(x1, len(ids) * 50, 0))
            status, lid = modelSpace.appendGcDbEntity(ln)
            ln.close()
            if status == Gcad.eOk:
                ids.append(lid)
        modelSpace.close()
        if len(ids) < 2:
            gcutPrintf("\n[SWEEP6 GROUP] FAIL: nie udało się utworzyć encji do grupy")
            return

        db = gcdbWorkingDatabase()
        status, gd = db.getGroupDictionary(GcDb.kForWrite)
        if status != Gcad.eOk:
            gcutPrintf("\n[SWEEP6 GROUP] FAIL: getGroupDictionary != eOk")
            return
        group = GcDbGroup("SWEEP6 grupa testowa")
        status, gid = gd.setAt("SWEEP6_GRP", group)
        gd.close()
        if status != Gcad.eOk:
            group.close()
            gcutPrintf(f"\n[SWEEP6 GROUP] FAIL: setAt != eOk ({status})")
            return
        appended = 0
        for oid in ids:
            group.append(oid)
            appended += 1
        group.close()
        gcutPrintf(f"\n[SWEEP6 GROUP] PASS — grupa SWEEP6_GRP utworzona, dodano {appended} encji")
    except Exception as err:
        gcutPrintf(f"\n[SWEEP6 GROUP] FAIL: {type(err).__name__}: {err}")


@command(local_name='SWEEP6_ALL')
def sweep6All():
    """Wszystkie cztery po kolei. Jeśli któryś crashuje/zatruwa sesję — użyj pojedynczych."""
    gcutPrintf("\n===== SWEEP6 START =====")
    verifyRgbLayer()
    verifyModelSpaceIteration()
    verify2dPolyline()
    verifyGroup()
    gcutPrintf("\n===== SWEEP6 KONIEC =====")
