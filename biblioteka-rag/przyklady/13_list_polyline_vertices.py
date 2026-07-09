# Wzorcowa komenda 13 — Wypisanie współrzędnych wierzchołków polilinii.
#
# Demonstruje wybór pojedynczej encji (gcedEntSel), sprawdzenie jej typu
# i iterację po jej wierzchołkach. Wzorzec kanoniczny z oficjalnego samples
# pliniter.py — dotyczy klasycznej polilinii 2D (GcDb2dPolyline, tzw. „ciężkiej"),
# która ma iterator wierzchołków (vertexIterator).
#
# WAŻNE: pliniter.py działa dla GcDb2dPolyline. Aby GstarCAD tworzył ten typ
# (a nie lekką GcDbPolyline), zmienna systemowa PLINETYPE musi być 0
# (polecenie: SETVAR PLINETYPE 0, potem narysuj polilinię). Odczyt wierzchołków
# lekkiej GcDbPolyline (numVerts/getPointAt) jest oznaczony 🔴 do weryfikacji
# na LC i zostanie dodany jako osobny wariant po potwierdzeniu API.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz WYPISZ_WIERZCHOLKI.
# Komenda poprosi o wskazanie polilinii 2D i wypisze współrzędne każdego
# wierzchołka w command line.
#
# Konwencje (v2 przewodnika + pliniter.py):
#   - gcedEntSel zwraca RTNORM przy wyborze; gcdbGetObjectId zamienia name→ObjectId
#   - isKindOf(GcDb2dPolyline.desc()) przed pracą na wierzchołkach
#   - vertexIterator() + done()/step(); wierzchołek to GcDb2dVertex.position()

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='WYPISZ_WIERZCHOLKI')
def listPolylineVertices():
    """Wybiera polilinię 2D i wypisuje współrzędne jej wierzchołków."""
    try:
        en = gds_name()
        pt = GcGePoint3d()
        rc = gcedEntSel("\nWskaż polilinię 2D: ", en, pt)
        if rc != RTNORM:
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        entId = GcDbObjectId()
        gcdbGetObjectId(entId, en)

        status, obj = gcdbOpenObject(entId, GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć wybranego obiektu.")
            return

        if not obj.isKindOf(GcDb2dPolyline.desc()):
            obj.close()
            gcutPrintf(
                "\nWybrany obiekt nie jest polilinią 2D (GcDb2dPolyline). "
                "Ustaw SETVAR PLINETYPE 0 przed rysowaniem polilinii."
            )
            return
        obj.close()

        # Iteracja po wierzchołkach (per pliniter.py)
        status, line = gcdbOpenObject(entId, GcDb.kForRead)
        vertIter = line.vertexIterator()
        line.close()

        count = 0
        while not vertIter.done():
            vertexId = vertIter.objectId()
            status, vObj = gcdbOpenObject(vertexId, GcDb.kForRead)
            vertex = GcDb2dVertex.cast(vObj)
            loc = vertex.position()
            vertex.close()
            gcutPrintf(f"\nWierzchołek #{count}: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")
            count += 1
            vertIter.step()

        gcutPrintf(f"\nŁącznie wierzchołków: {count}")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy wypisywaniu wierzchołków: {err}")
