from pygcad.core import *
from pygcad.pygrx import *

def rysujProstokatZWymiarami():
    try:
        # Parametry prostokąta
        szerokosc = 1000
        wysokosc = 600

        # Wierzchołki prostokąta
        p1 = GcGePoint2d(0, 0)
        p2 = GcGePoint2d(szerokosc, 0)
        p3 = GcGePoint2d(szerokosc, wysokosc)
        p4 = GcGePoint2d(0, wysokosc)

        database = gcdbWorkingDatabase()
        status, blockTable = database.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        # Rysowanie zamkniętej polilinii - prostokąta
        pline = GcDbPolyline()
        pline.addVertexAt(0, p1, 0, 0, 0)
        pline.addVertexAt(1, p2, 0, 0, 0)
        pline.addVertexAt(2, p3, 0, 0, 0)
        pline.addVertexAt(3, p4, 0, 0, 0)
        pline.setClosed(True)

        status, plineId = modelSpace.appendGcDbEntity(pline)
        pline.close()

        # Wymiar liniowy dla boku poziomego (dolny bok, od p1 do p2)
        odsuniecieDol = -80  # przesunięcie linii wymiarowej poniżej prostokąta
        tekstPunktDol = GcGePoint3d(szerokosc / 2, odsuniecieDol, 0)
        wymiarPoziomy = GcDbAlignedDimension(
            GcGePoint3d(p1.x, p1.y, 0),
            GcGePoint3d(p2.x, p2.y, 0),
            tekstPunktDol,
            ""
        )
        wymiarPoziomy.setDimscale(40)   # skala wymiaru: tekst/strzalki widoczne na obiekcie ~1000 j.
        status, wymPoziomyId = modelSpace.appendGcDbEntity(wymiarPoziomy)
        wymiarPoziomy.close()

        # Wymiar liniowy dla boku pionowego (lewy bok, od p1 do p4)
        odsuniecieLewo = -150  # przesunięcie linii wymiarowej na lewo od prostokąta
        tekstPunktLewo = GcGePoint3d(odsuniecieLewo, wysokosc / 2, 0)
        wymiarPionowy = GcDbAlignedDimension(
            GcGePoint3d(p1.x, p1.y, 0),
            GcGePoint3d(p4.x, p4.y, 0),
            tekstPunktLewo,
            ""
        )
        wymiarPionowy.setDimscale(40)   # skala wymiaru: tekst/strzalki widoczne na obiekcie ~1000 j.
        status, wymPionowyId = modelSpace.appendGcDbEntity(wymiarPionowy)
        wymiarPionowy.close()

        modelSpace.close()

        gcedPrompt("\nProstokąt 1000x600 z wymiarami narysowany pomyślnie.")
    except Exception as err:
        gcedPrompt('\n[BŁĄD]: %s' % err)

rysujProstokatZWymiarami()
