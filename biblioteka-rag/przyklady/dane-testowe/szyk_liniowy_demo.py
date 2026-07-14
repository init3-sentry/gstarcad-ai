# DEMO POKAZOWE — szyk liniowy „jak w SketchUpie" (skopiuj raz w kierunku + ×N).
#
# ⚠️ To jest DEMO, żeby ZOBACZYĆ o co chodzi — NIE narzędzie produkcyjne. GstarCAD robi
#    to natywnie (COPY z opcją równoodległość/podział, oraz ARRAYRECT). Zgodnie z REGUŁĄ #0
#    nie dublujemy funkcji natywnej. Cel demka: porównać „feel" z natywnym ARRAY.
#
# Mechanika (rdzeń pomysłu, kilkanaście linii): weź obiekt -> złap wektor z dwóch punktów
#    -> sklonuj i przesuń kumulacyjnie ×i, N razy. Działa na PROSTYCH obiektach
#    (linia / okrąg / polilinia / tekst).
#
# Uzycie: APPLOAD, potem SZYK_LINIOWY. Wskaż obiekt, punkt bazowy, drugi punkt (kierunek
#    i odległość jednego skoku), podaj łączną liczbę sztuk.

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='SZYK_LINIOWY')
def szykLiniowy():
    try:
        # 1) wybór obiektu
        en = gds_name()
        pt = gds_point()
        if gcedEntSel("\nWskaz obiekt do powielenia: ", en, pt) != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        entId = GcDbObjectId()
        gcdbGetObjectId(entId, en)

        # 2) wektor skoku = drugi punkt - punkt bazowy
        p1 = GcGePoint3d()
        if gcedGetPoint(None, "\nPunkt bazowy: ", p1) != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        p2 = GcGePoint3d()
        if gcedGetPoint(p1, "\nKierunek + odleglosc jednego skoku (drugi punkt): ", p2) != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        dx, dy, dz = p2.x - p1.x, p2.y - p1.y, p2.z - p1.z

        # 3) łączna liczba sztuk
        status, total = gcedGetInt("\nLaczna liczba sztuk z oryginalem (np. 5): ")
        if status != RTNORM or total < 2:
            gcutPrintf("\nAnulowano (potrzeba min. 2).")
            return

        db = gcdbWorkingDatabase()
        s, src = gcdbOpenObject(entId, GcDb.kForRead)
        if s != Gcad.eOk or src is None:
            gcutPrintf("\n[BLAD] nie otwarto obiektu.")
            return
        srcEnt = GcDbEntity.cast(src)
        if srcEnt is None:
            src.close()
            gcutPrintf("\n[BLAD] wskazany obiekt to nie encja.")
            return

        s, bt = db.getBlockTable(GcDb.kForRead)
        s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        bt.close()

        made = 0
        for i in range(1, total):
            clone = GcDbEntity.cast(srcEnt.clone())
            if clone is None:
                continue
            mat = GcGeMatrix3d()
            mat.setToTranslation(GcGeVector3d(dx * i, dy * i, dz * i))
            clone.transformBy(mat)
            ms.appendGcDbEntity(clone)
            clone.close()
            made += 1

        srcEnt.close()
        ms.close()
        gcutPrintf(f"\nSzyk liniowy: dodano {made} kopii (razem {made + 1} sztuk).")

    except Exception as err:
        gcutPrintf(f"\n[BLAD] szyk: {err}")
