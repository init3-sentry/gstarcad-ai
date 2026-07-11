from pygcad.core import *
from pygcad.pygrx import *

def rysujSiatkeOsi():
    try:
        db = gcdbWorkingDatabase()
        status, blockTable = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTable.close()

        promien = 120
        rozstaw = 500
        # Zasięg siatki
        szerX = 3 * rozstaw  # 4 osie pionowe: 0,500,1000,1500
        szerY = 2 * rozstaw  # 3 osie poziome: 0,500,1000

        zapasStart = 300      # ile linia wystaje poza pierwszą/ostatnią oś
        zapasKoniecKolko = promien + 100  # miejsce na kółko z opisem

        etykietyPionowe = ["A", "B", "C", "D"]
        etykietyPoziome = ["1", "2", "3"]

        # --- Osie pionowe (linie biegnące w kierunku Y) ---
        for i, etykieta in enumerate(etykietyPionowe):
            x = i * rozstaw
            yStart = -zapasStart
            yKoniec = szerY + zapasKoniecKolko

            linia = GcDbLine(GcGePoint3d(x, yStart, 0), GcGePoint3d(x, yKoniec, 0))
            status, objId = modelSpace.appendGcDbEntity(linia)
            linia.close()

            # Kółko z opisem na końcu osi
            srodekKolka = GcGePoint3d(x, yKoniec, 0)
            kolko = GcDbCircle(srodekKolka, GcGeVector3d(0, 0, 1), promien)
            status, objId = modelSpace.appendGcDbEntity(kolko)
            kolko.close()

            # Etykieta wyśrodkowana w kółku
            txt = GcDbText(srodekKolka, etykieta)
            txt.setHeight(promien * 0.8)
            txt.setHorizontalMode(GcDb.TextHorzMode.kTextCenter)
            txt.setVerticalMode(GcDb.TextVertMode.kTextVertMid)
            txt.setAlignmentPoint(srodekKolka)
            status, objId = modelSpace.appendGcDbEntity(txt)
            txt.close()

        # --- Osie poziome (linie biegnące w kierunku X) ---
        for j, etykieta in enumerate(etykietyPoziome):
            y = j * rozstaw
            xStart = -zapasKoniecKolko
            xKoniec = szerX + zapasStart

            linia = GcDbLine(GcGePoint3d(xStart, y, 0), GcGePoint3d(xKoniec, y, 0))
            status, objId = modelSpace.appendGcDbEntity(linia)
            linia.close()

            # Kółko z opisem na początku osi (lewa strona)
            srodekKolka = GcGePoint3d(xStart, y, 0)
            kolko = GcDbCircle(srodekKolka, GcGeVector3d(0, 0, 1), promien)
            status, objId = modelSpace.appendGcDbEntity(kolko)
            kolko.close()

            txt = GcDbText(srodekKolka, etykieta)
            txt.setHeight(promien * 0.8)
            txt.setHorizontalMode(GcDb.TextHorzMode.kTextCenter)
            txt.setVerticalMode(GcDb.TextVertMode.kTextVertMid)
            txt.setAlignmentPoint(srodekKolka)
            status, objId = modelSpace.appendGcDbEntity(txt)
            txt.close()

        modelSpace.close()
        gcedPrompt("\nSiatka osi konstrukcyjnych narysowana (4 osie pionowe A-D, 3 osie poziome 1-3).")
    except Exception as err:
        gcedPrompt('\n[BŁĄD]: %s' % err)

rysujSiatkeOsi()
