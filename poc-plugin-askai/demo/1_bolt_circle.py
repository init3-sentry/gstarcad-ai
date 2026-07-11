from pygcad.core import *
from pygcad.pygrx import *
import math

def rysuj_rozstaw_srub():
    try:
        database = gcdbWorkingDatabase()
        status, blockTable = database.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        cx, cy = 0.0, 0.0
        promien_podzialowy = 400.0
        promien_sruby = 20.0
        liczba_srub = 8

        # Okrąg podziałowy (linia odniesienia rozstawu śrub)
        okrag_podzialowy = GcDbCircle(GcGePoint3d(cx, cy, 0), GcGeVector3d(0, 0, 1), promien_podzialowy)
        okrag_podzialowy.setColorIndex(1)  # czerwony
        status, oid = modelSpace.appendGcDbEntity(okrag_podzialowy)
        okrag_podzialowy.close()

        # Krzyż środka
        dl_kreski = promien_podzialowy * 0.1
        linia1 = GcDbLine(GcGePoint3d(cx - dl_kreski, cy, 0), GcGePoint3d(cx + dl_kreski, cy, 0))
        linia1.setColorIndex(1)
        status, oid = modelSpace.appendGcDbEntity(linia1)
        linia1.close()

        linia2 = GcDbLine(GcGePoint3d(cx, cy - dl_kreski, 0), GcGePoint3d(cx, cy + dl_kreski, 0))
        linia2.setColorIndex(1)
        status, oid = modelSpace.appendGcDbEntity(linia2)
        linia2.close()

        # Osiem śrub rozmieszczonych równomiernie na okręgu podziałowym
        for i in range(liczba_srub):
            kat = 2 * math.pi * i / liczba_srub
            sx = cx + promien_podzialowy * math.cos(kat)
            sy = cy + promien_podzialowy * math.sin(kat)

            sruba = GcDbCircle(GcGePoint3d(sx, sy, 0), GcGeVector3d(0, 0, 1), promien_sruby)
            sruba.setColorIndex(5)  # niebieski
            status, oid = modelSpace.appendGcDbEntity(sruba)
            sruba.close()

        modelSpace.close()
        gcedPrompt("\nNarysowano rozstaw 8 śrub na okręgu podziałowym R=400.")
    except Exception as err:
        gcedPrompt('\n[BŁĄD]: %s' % err)

rysuj_rozstaw_srub()
