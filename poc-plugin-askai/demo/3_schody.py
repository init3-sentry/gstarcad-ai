from pygcad.core import *
from pygcad.pygrx import *

def rysuj_rzut_schodow():
    # Rysuje rzut biegu schodów: 10 równoległych linii stopni co 300 jednostek,
    # szerokość biegu 1200, oraz linia biegu (kreska ukosna) po środku
    try:
        database = gcdbWorkingDatabase()
        status, blockTable = database.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        liczba_stopni = 10
        rozstaw = 300
        szerokosc = 1200

        # Linie stopni - równoległe, prostopadłe do kierunku biegu (oś X)
        for i in range(liczba_stopni + 1):
            y = i * rozstaw
            linia = GcDbLine(GcGePoint3d(0, y, 0), GcGePoint3d(szerokosc, y, 0))
            status, objId = modelSpace.appendGcDbEntity(linia)
            linia.close()

        # Linie boczne biegu (krawędzie szerokości)
        lewa = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(0, liczba_stopni * rozstaw, 0))
        status, objId = modelSpace.appendGcDbEntity(lewa)
        lewa.close()

        prawa = GcDbLine(GcGePoint3d(szerokosc, 0, 0), GcGePoint3d(szerokosc, liczba_stopni * rozstaw, 0))
        status, objId = modelSpace.appendGcDbEntity(prawa)
        prawa.close()

        # Linia biegu po środku (linia łamania, symbolicznie ukośna przez cały bieg)
        srodek_x = szerokosc / 2.0
        dl_ukosu = 150  # długość odsunięcia charakterystycznej "kreski" linii biegu
        punkt_start = GcGePoint3d(srodek_x - dl_ukosu, 0 - dl_ukosu, 0)
        punkt_koniec = GcGePoint3d(srodek_x + dl_ukosu, liczba_stopni * rozstaw + dl_ukosu, 0)
        linia_biegu = GcDbLine(punkt_start, punkt_koniec)
        status, objId = modelSpace.appendGcDbEntity(linia_biegu)
        linia_biegu.close()

        modelSpace.close()
        gcedPrompt("\nRzut biegu schodów narysowany: 10 stopni co 300, szerokość 1200.")
    except Exception as err:
        gcedPrompt('\n[BŁĄD]: %s' % err)

rysuj_rzut_schodow()
